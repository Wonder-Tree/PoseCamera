import tensorflow as tf
import numpy as np
import cv2
import wget
import os

keypoints_names = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", 
    "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", 
    "right_knee", "left_ankle", "right_ankle"
]

class Pose: 
    def __init__(self, keypoints) -> None:
        self.keypoints = {}
        for i in range(0, 17):
            self.keypoints[
                keypoints_names[i]
            ] = keypoints[i]
        

class PoseTracker:
    def __init__(self, pose_model=None) -> None:
        self.input_size = 192

        if pose_model is None:
            pose_model = os.path.join(
                os.path.dirname(__file__) + "/lite-model_movenet_singlepose_lightning_3.tflite"
            )
            if not os.path.isfile(pose_model):
                self.download_pretained_models(pose_model)
        
        self.interpreter = tf.lite.Interpreter(model_path=pose_model)
        self.interpreter.allocate_tensors()

    @staticmethod
    def download_pretained_models(pose_model):
        wget.download(
            "https://storage.googleapis.com/wt_storage/lite-model_movenet_singlepose_lightning_3.tflite",
            pose_model
        )

    def preprocess_img(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image = tf.convert_to_tensor(rgb, dtype=tf.float32)
        input_image = tf.expand_dims(image, axis=0)
        input_image = tf.image.resize(input_image, (self.input_size, self.input_size))
        return input_image

    def __call__(self, img):
        input_image = self.preprocess_img(img)

        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        self.interpreter.set_tensor(input_details[0]['index'], input_image)
        self.interpreter.invoke()

        keypoints = np.squeeze(
            self.interpreter.get_tensor(output_details[0]['index'])
        )

        for keypoint in keypoints:
            keypoint[0] *= img.shape[0] 
            keypoint[1] *= img.shape[1]

        return Pose(keypoints)
