import argparse
import os

import cv2
import numpy as np

from posecamera.modules.file_providers import ImageReader, VideoReader
from posecamera import pose_tracker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=str, default=None, help='path to video file or camera id')
    parser.add_argument('--images', nargs='+', default=None, help='path to input image(s)')
    parser.add_argument('--cpu', action='store_true', help='run network inference on cpu')
    parser.add_argument('--no-display', action='store_true', help='hide gui')

    args = parser.parse_args()

    if args.video is None and args.images is None:
        raise ValueError('--video or --image has to be provided ')

    
    if args.video:
        frame_provider = VideoReader(args.video)
    else:
        frame_provider = ImageReader(args.images)
    
    det = pose_tracker.PoseTracker()

    for frame in frame_provider:
        pose = det(frame)

        if not args.no_display:
            for (name, (y, x, score)) in pose.keypoints.items():
                cv2.circle(frame, (int(x), int(y)), 3, (255, 0, 0), -1)
            
            cv2.imshow("PoseCamera", frame)
            if cv2.waitKey(1) == 27:
                break
        else:
            print(
                pose.keypoints
            )



if __name__ == "__main__":
    main()