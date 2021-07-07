import csv
import cv2
import numpy as np
import tensorflow as tf
from shapely.geometry import Polygon
from scipy.spatial.distance import pdist, squareform
import wget
import os

class HandTracker():
    def __init__(self, 
                 palm_model=None, 
                 joint_model=None, 
                 anchors_path=None,
                 box_enlarge = 1.5, 
                 box_shift = 0.4, 
                 max_hands = 2,
                 detect_hand_thres = 0.7,
                 detect_keypoints_thres = 0.2,
                 iou_thres = 0.6,
                 independent = False
                 ):
        
        # Flags
        self.independent = independent
        
        # BBox predictions parameters
        self.box_shift = box_shift
        self.box_enlarge = box_enlarge
        
        # HandLanmarks parameters (not used for now)
        self.max_hands = max_hands
        self.is_hands_list = [False]*max_hands
        
        # Initialise previous frame buffers
        self.bb_prev = [None]*max_hands
        self.kp_prev = [None]*max_hands
        
        # Thresholds init
        self.detect_hand_thres = detect_hand_thres
        self.detect_keypoints_thres = detect_keypoints_thres
        self.iou_thres = iou_thres

        # Initialise models
        if palm_model is None:
            palm_model = os.path.join(
                os.path.dirname(__file__) + "/palm_detection_without_custom_op.tflite"
            )
            if not os.path.isfile(palm_model):
                self.download_pretained_models("palm_model", palm_model)

        if joint_model is None:
            joint_model = os.path.join(
                os.path.dirname(__file__) + "/hand_landmark.tflite"
            )
            if not os.path.isfile(joint_model):
                self.download_pretained_models("joint_model", joint_model)

        if anchors_path is None:
            anchors_path = os.path.join(
                os.path.dirname(__file__) + "/anchors.csv"
            )
            if not os.path.isfile(anchors_path):
                self.download_pretained_models("anchors_path", anchors_path)
            

        self.interp_palm = tf.lite.Interpreter(palm_model)
        self.interp_palm.allocate_tensors()
        self.interp_joint = tf.lite.Interpreter(joint_model)
        self.interp_joint.allocate_tensors()
        
        # reading the SSD anchors
        with open(anchors_path, "r") as csv_f:
            self.anchors = np.r_[
                [x for x in csv.reader(csv_f, quoting=csv.QUOTE_NONNUMERIC)]
            ]
        # reading tflite model paramteres
        output_details = self.interp_palm.get_output_details()
        input_details = self.interp_palm.get_input_details()
        
        # Getting tensor index for palm detection
        self.in_idx = input_details[0]['index']
        self.out_reg_idx = output_details[0]['index']
        self.out_clf_idx = output_details[1]['index']
        
        # Getting tensor index for hand landmarks
        self.in_idx_joint = self.interp_joint.get_input_details()[0]['index']
        self.out_idx_joint = self.interp_joint.get_output_details()[0]['index']
        self.out_idx_is_hand = self.interp_joint.get_output_details()[1]['index']

        # 90° rotation matrix used to create the alignment trianlge        
        self.R90 = np.r_[[[0,1],[-1,0]]]

        # trianlge target coordinates used to move the detected hand
        # into the right position
        self._target_triangle = np.float32([
                        [128, 128],
                        [128,   0],
                        [  0, 128]
                    ])
        self._target_box = np.float32([
                        [  0,   0, 1],
                        [256,   0, 1],
                        [256, 256, 1],
                        [  0, 256, 1],
                    ])
    
    def _get_triangle(self, kp0, kp2, dist=1):
        dir_v = kp2 - kp0
        dir_v /= np.linalg.norm(dir_v)

        dir_v_r = dir_v @ self.R90.T
        return np.float32([kp2, kp2+dir_v*dist, kp2 + dir_v_r*dist])

    @staticmethod
    def download_pretained_models(model, output):
        if model == "palm_model":
            wget.download("https://storage.googleapis.com/wt_storage/palm_detection_without_custom_op.tflite", output)
        if model == "joint_model":
            wget.download("https://storage.googleapis.com/wt_storage/hand_landmark.tflite", output)
        if model == "anchors_path":
            wget.download("https://storage.googleapis.com/wt_storage/anchors.csv", output)

    @staticmethod
    def _triangle_to_bbox(source):
        # plain old vector arithmetics
        bbox = np.c_[
            [source[2] - source[0] + source[1]],
            [source[1] + source[0] - source[2]],
            [3 * source[0] - source[1] - source[2]],
            [source[2] - source[1] + source[0]],
        ].reshape(-1,2)
        return bbox
    
    @staticmethod
    def _im_normalize(img):
         return np.ascontiguousarray(
             2 * ((img / 255) - 0.5
        ).astype('float32'))
       
    @staticmethod
    def _sigm(x):
        return 1 / (1 + np.exp(-x) )
    
    @staticmethod
    def _pad1(x):
        return np.pad(x, ((0,0),(0,1)), constant_values=1, mode='constant')
    
    @staticmethod
    def _IOU(poly1, poly2):
        return poly1.intersection(poly2).area / poly1.union(poly2).area
    
    @staticmethod
    def _max_dist(points):
        D = pdist(points)
        D = squareform(D);
        return np.nanmax(D)
    
    def _predict_bbox(self, kp, bbox):
        kp_C = kp[9]
        bb_C = bbox.sum(axis = 0)/len(bbox)
        bbox_pred = bbox + (kp_C - bb_C)

        line = np.array([kp[0], kp[9]])
        bbox_side = bbox[1] - bbox[2]
        line_vec = line[1] - line[0]
        cangle = np.dot(line_vec, bbox_side)/(np.linalg.norm(line_vec) * np.linalg.norm(bbox_side))
        sangle = np.sqrt(1 - cangle*cangle)

        scale = self.box_enlarge * self._max_dist(kp)/np.linalg.norm(bbox_side)
        rot = np.r_[[[cangle,-sangle],[sangle,cangle]]]
        bbox_pred = (bbox - bb_C) @ rot * scale + bb_C
        
        return bbox_pred
    
    def _GetCandidateIdx(self, box_list, max_hands = 2, iou_thres = 0.45):    
        box_groups = [[(box_list[0], 0)]]

        # Group BBOX according to IOU
        for idx, box in enumerate(box_list[1:]):
            idx += 1
            pbox = Polygon(box)
            new_group = True
            for group in box_groups:
                if self._IOU(pbox, Polygon(group[0][0])) > iou_thres:
                    group.append((box, idx))
                    new_group = False
                    break
            if new_group: 
                box_groups.append([(box, idx)])

        len_groups = [(len(group), idx) for idx, group in enumerate(box_groups)]
        len_groups = sorted(len_groups, reverse = True, key = lambda x: x[0])

        candidate_groups_idx = [len_idx[-1] for len_idx in len_groups[:max_hands]]
        candidate_groups = [box_groups[idx] for idx in candidate_groups_idx]

        candidate_groups_area = [[(Polygon(box).area, idx) for box, idx in group] for group in candidate_groups]
        candidate_idx = [max(group, key=lambda x: x[0])[-1] for group in candidate_groups_area]

        return candidate_idx
    
    def _source_to_bbox(self, scale, pad, source):
        Mtr = cv2.getAffineTransform(
                source * scale,
                self._target_triangle
                )
        
        Mtr_temp = self._pad1(Mtr.T).T
        Mtr_temp[2,:2] = 0
        Minv = np.linalg.inv(Mtr_temp)
        
        box_orig = (self._target_box @ Minv.T)[:,:2]
        box_orig -= pad[::-1]
        
        return box_orig, Mtr, Minv
    
    def _bbox_to_source(self, bbox, pad):
        src_tri = np.array(bbox[:3] + pad[::-1], dtype=np.float32)
        dst_tri = self._target_box[:3,:2].copy(order='C')
        Mtr = cv2.getAffineTransform(src_tri, dst_tri)

        Mtr_temp = self._pad1(Mtr.T).T
        Mtr_temp[2,:2] = 0
        Minv = np.linalg.inv(Mtr_temp)
        
        return Mtr, Minv
    
    def _get_bbox_Mtr_Minv(self, img, img_norm):
        source_list = self.detect_hand(img_norm)
        if len(source_list) == 0:
            return [], []

        scale = max(img.shape) / 256
        bbox_Mtr_Minv_list = [self._source_to_bbox(scale, self.pad, source) for source in source_list]
        box_orig_list = [ele[0] for ele in bbox_Mtr_Minv_list]

        box_valid_idx = self._GetCandidateIdx(box_orig_list, max_hands = self.max_hands, iou_thres = self.iou_thres)
        box_orig_list = [box_orig_list[i] for i in box_valid_idx]
        Mtr_Minv_list = [bbox_Mtr_Minv_list[i][1:] for i in box_valid_idx]

        box_orig_list += [None] * (self.max_hands - len(box_orig_list))
        Mtr_Minv_list += [(None, None)] * (self.max_hands - len(Mtr_Minv_list))
        
        return box_orig_list, Mtr_Minv_list
    
    def _merge_bbox_predicts(self, bbox_list, bbox_params):
        prev_poly = [Polygon(box) for box in self.bb_prev]
        curr_poly = [Polygon(box) for box in bbox_list]
        
        rearranged_box = [None]*self.max_hands
        rearranged_params = [None]*self.max_hands
        leftover = curr_poly[:]
        for idx1, ppoly in enumerate(prev_poly):
            for idx2, cpoly in enumerate(curr_poly):
                if cpoly in leftover: continue
                if self._IOU(ppoly, cpoly) > self.iou_thres:
                    rearranged_box[idx1] = self.bb_prev[idx2]
                    rearranged_params[idx1] = tuple(_bbox_to_source(bbox, self.pad))
                    leftover[idx2] = None
                    break
        
        leftover = [i for i in leftover if type(i) != type(None)]
        
        for idx1, cpoly in enumerate(leftover):
            for idx2 in range(len(rearranged_box)):
                if type(rearranged_box[idx2]) == type(None):
                    rearranged_box[idx2] = bbox_list[idx1]
                    rearranged_params[idx2] = bbox_params[idx1]
                    break
        
        return rearranged_box, rearranged_params
        
    
    def predict_joints(self, img_norm, hand_thres = 0.):
        self.interp_joint.set_tensor(
            self.in_idx_joint, img_norm.reshape(1,256,256,3))
        self.interp_joint.invoke()

        joints = self.interp_joint.get_tensor(self.out_idx_joint)
        is_hand = self.interp_joint.get_tensor(self.out_idx_is_hand)[0][0]*10**11
        
        return joints.reshape(-1,2), is_hand > hand_thres

    def detect_hand(self, img_norm):
        '''Perform palm hand detection'''
        
        assert -1 <= img_norm.min() and img_norm.max() <= 1,\
        "img_norm should be in range [-1, 1]"
        assert img_norm.shape == (256, 256, 3),\
        "img_norm shape must be (256, 256, 3)"

        # predict hand location and 7 initial landmarks
        self.interp_palm.set_tensor(self.in_idx, img_norm[None])
        self.interp_palm.invoke()

        out_reg = self.interp_palm.get_tensor(self.out_reg_idx)[0]
        out_clf = self.interp_palm.get_tensor(self.out_clf_idx)[0,:,0]
        
        # finding the best prediction
        detecion_mask = self._sigm(out_clf.astype(np.float64)) > self.detect_hand_thres
        candidate_detect = out_reg[detecion_mask]
        candidate_anchors = self.anchors[detecion_mask]

        if candidate_detect.shape[0] == 0:
            return []
        
        candidate_idx = list(range(candidate_detect.shape[0]))

        # bounding box offsets, width and height
        bbox_dets_list = []
        center_wo_offst_list = []
        for idx in candidate_idx:
            dx,dy,w,h = candidate_detect[idx, :4]
            bbox_dets_list.append((dx,dy,w,h))
            
            center_wo_offst_list.append(candidate_anchors[idx,:2] * 256)
        
        keypoints_list = [center_wo_offst_list[i] + candidate_detect[idx,4:].reshape(-1,2) for i,idx in enumerate(candidate_idx)]
        side_list = [max(w,h) * self.box_enlarge for _,_,w,h in bbox_dets_list]
        
        source_list = [self._get_triangle(keypoints[0], keypoints[2], side) for keypoints, side in zip(keypoints_list, side_list)]
        source_list = [source - (keypoints[0] - keypoints[2]) * self.box_shift for source, keypoints in zip(source_list, keypoints_list)]
        source_list = [np.array(source, dtype="float32") for source in source_list]
        
        return source_list

    def preprocess_img(self, img):
        shape = np.r_[img.shape]
        pad = (shape.max() - shape[:2]).astype('uint32') // 2
        img_pad = np.pad(
            img,
            ((pad[0],pad[0]), (pad[1],pad[1]), (0,0)),
            mode='constant')
        img_small = cv2.resize(img_pad, (256, 256))
        img_small = np.ascontiguousarray(img_small)
        
        img_norm = self._im_normalize(img_small)
        return img_pad, img_norm, pad


    def __call__(self, img, get_kp = True):
        # Process image
        img_pad, img_norm, pad = self.preprocess_img(img)
        self.pad = pad
        
        # Checks whether to recompute palm detection or use previous frame's bounding box
        if len([1 for i in self.bb_prev if type(i) == type(None)]) > 0:
            box_orig_list, Mtr_Minv_list = self._get_bbox_Mtr_Minv(img, img_norm)
            box_orig_list, Mtr_Minv_list = self._merge_bbox_predicts(box_orig_list, Mtr_Minv_list)
            
            if not get_kp: return [], box_orig_list
        else:
            box_orig_list = [self._predict_bbox(kp, bbox) for kp, bbox in zip(self.kp_prev, self.bb_prev)]
            Mtr_Minv_list = [self._bbox_to_source(bbox, pad) for bbox in box_orig_list]
        
        
        # Initialise buffers
        is_hands_list_prev = self.is_hands_list
        kp_orig_list = []
        self.is_hands_list = []
        index = 0
            
        kp_orig_list = []
        
        # Iterate across all palm detections
        for Mtr, Minv in Mtr_Minv_list:
            
            # Check if palm instance exist
            if type(Mtr) == type(None):
                self.is_hands_list.append(False)
                kp_orig_list.append(None)
                continue

            # Crop image according to bounding box
            img_landmark = cv2.warpAffine(
                self._im_normalize(img_pad), Mtr, (256,256)
            )
            
            # Get hand keypoints. is_hand is to detect if hand is present within bounding box
            joints, is_hand = self.predict_joints(img_landmark, hand_thres = self.detect_keypoints_thres)
            if not is_hand:
                self.is_hands_list.append(False)
                box_orig_list[index] = None
                kp_orig_list.append(None)
                is_recall = True
                continue

            # projecting keypoints back into original image coordinate space
            kp_orig = (self._pad1(joints) @ Minv.T)[:,:2]
            kp_orig -= pad[::-1]
            
            kp_orig_list.append(kp_orig)
            self.is_hands_list.append(is_hand)
            
            index += 1
        
        # Store previous frame bbox and kp
        if not self.independent:
            self.bb_prev = box_orig_list
            self.kp_prev = kp_orig_list
        
        # Recall if is_hands has changed (The number of palm instances decreased)
        if (len([1 for i,j in zip(is_hands_list_prev, self.is_hands_list) if (i==True and j==False)]) != 0):
            return self.__call__(img, get_kp = get_kp)
        
        return kp_orig_list, box_orig_list
