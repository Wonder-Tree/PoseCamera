
import cv2
import numpy as np
import torch
import wget
import os

from .models.with_mobilenet import PoseEstimationWithMobileNet
from .modules.keypoints import extract_keypoints, group_keypoints
from .modules.load_state import load_state
from .modules.pose import Pose, track_poses
from .val import normalize, pad_width

weights = os.path.join(os.path.expanduser("~"),'.posecamera','checkpoint_iter.pth')
if not os.path.exists(weights):
    os.makedirs(os.path.dirname(weights), exist_ok=True)
    wget.download("https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth", weights)

net = PoseEstimationWithMobileNet()
checkpoint = torch.load(weights, map_location='cpu')
load_state(net, checkpoint)

stride = 8
upsample_ratio = 4
num_keypoints = Pose.num_kpts
cpu = True
smooth = True

def config(stride = 8, upsample_ratio = 4, smooth = True,  cpu = True):
    stride = stride
    upsample_ratio = upsample_ratio
    smooth = smooth
    cpu = cpu

    global net
    if not cpu:
        net = net.cuda()
    else:
        net = net.eval()

def _inference(net, img, net_input_height_size, stride, upsample_ratio, cpu, 
               pad_value=(0, 0, 0), img_mean=(128, 128, 128), img_scale=1/256):
    height, width, _ = img.shape
    scale = net_input_height_size / height

    scaled_img = cv2.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    scaled_img = normalize(scaled_img, img_mean, img_scale)
    min_dims = [net_input_height_size, max(scaled_img.shape[1], net_input_height_size)]
    padded_img, pad = pad_width(scaled_img, stride, pad_value, min_dims)

    tensor_img = torch.from_numpy(padded_img).permute(2, 0, 1).unsqueeze(0).float()
    if not cpu:
        tensor_img = tensor_img.cuda()

    stages_output = net(tensor_img)

    stage2_heatmaps = stages_output[-2]
    heatmaps = np.transpose(stage2_heatmaps.squeeze().cpu().data.numpy(), (1, 2, 0))
    heatmaps = cv2.resize(heatmaps, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    stage2_pafs = stages_output[-1]
    pafs = np.transpose(stage2_pafs.squeeze().cpu().data.numpy(), (1, 2, 0))
    pafs = cv2.resize(pafs, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    return heatmaps, pafs, scale, pad

def estimate(img, height_size = 256):
    global net
    heatmaps, pafs, scale, pad = _inference(net, img, height_size, stride, upsample_ratio, cpu)
    total_keypoints_num = 0
    all_keypoints_by_type = []
    for kpt_idx in range(num_keypoints): 
        total_keypoints_num += extract_keypoints(heatmaps[:, :, kpt_idx], all_keypoints_by_type, total_keypoints_num)

    pose_entries, all_keypoints = group_keypoints(all_keypoints_by_type, pafs, demo=True)
    for kpt_id in range(all_keypoints.shape[0]):
        all_keypoints[kpt_id, 0] = (all_keypoints[kpt_id, 0] * stride / upsample_ratio - pad[1]) / scale
        all_keypoints[kpt_id, 1] = (all_keypoints[kpt_id, 1] * stride / upsample_ratio - pad[0]) / scale
    current_poses = []
    for n, pose_entry in enumerate(pose_entries):
        if len(pose_entry) == 0:
            continue
        pose_keypoints = np.ones((num_keypoints, 2), dtype=np.int32) * -1
        for kpt_id in range(num_keypoints):
            if pose_entry[kpt_id] != -1.0:
                pose_keypoints[kpt_id, 0] = int(all_keypoints[int(pose_entry[kpt_id]), 0])
                pose_keypoints[kpt_id, 1] = int(all_keypoints[int(pose_entry[kpt_id]), 1])
        pose = Pose(pose_keypoints, pose_entry[18])
        current_poses.append(pose)
    
    return current_poses