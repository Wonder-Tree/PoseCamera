import argparse
import os

import cv2
import numpy as np
import torch
from werkzeug.utils import secure_filename

from modules.file_providers import ImageReader, VideoReader
from posecamera.api import config, estimate
from modules.pose import Pose, track_poses


from flask import Flask, request, render_template, json

app = Flask(__name__)

UPLOAD_DIR = './tmp'

@app.route('/', methods=['GET', 'POST'])
def detect():
    global args
    if request.method == 'GET':
        return render_template('docs.html')
    else:
        image_files = []
        for name in request.files:
            file = request.files[name]
            file_path = os.path.join(UPLOAD_DIR, secure_filename(file.filename))

            file.save(file_path)
            image_files.append(file_path)

        pose_results = run_inference(net, ImageReader(image_files), args.height_size, args.cpu, args.track, args.smooth, args.no_display, True)
        pose_keypoints = [pose.keypoints.tolist() for pose in pose_results]

        return app.response_class(
            response=json.dumps(pose_keypoints),
            mimetype='application/json'
        )


def run_inference(image_provider, height_size, track, no_display, json_view = False):
    previous_poses = []
    delay = 10

    if isinstance(image_provider, ImageReader):
        delay = 0

    for img in image_provider:
        current_poses = estimate(img, height_size)

        if json_view == True:
            return current_poses

        if not no_display:
            if track:
                track_poses(previous_poses, current_poses, smooth=smooth)
                previous_poses = current_poses
            for pose in current_poses:
                pose.draw(img)
                
            for pose in current_poses:
                cv2.rectangle(img, (pose.bbox[0], pose.bbox[1]),
                              (pose.bbox[0] + pose.bbox[2], pose.bbox[1] + pose.bbox[3]), (32, 202, 252))
                if track:
                    cv2.putText(img, 'id: {}'.format(pose.id), (pose.bbox[0], pose.bbox[1] - 16),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
            cv2.imshow('PoseCamera', img)
            key = cv2.waitKey(delay)
            if key == 27:
                return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint-path', type=str, default='./checkpoint_iter_50000.pth', help='path to the checkpoint')
    parser.add_argument('--height-size', type=int, default=256, help='network input layer height size')
    parser.add_argument('--video', type=str, default='', help='path to video file or camera id')
    parser.add_argument('--images', nargs='+', default='', help='path to input image(s)')
    parser.add_argument('--cpu', action='store_true', help='run network inference on cpu')
    parser.add_argument('--track', type=int, default=0, help='track pose id in video')
    parser.add_argument('--smooth', type=int, default=1, help='smooth pose keypoints')
    parser.add_argument('--no-display', action='store_true', help='hide gui')
    parser.add_argument('--http-server', action='store_true', help='starts http server')
    parser.add_argument('--port', type=int, default=8080, help='http server port')

    args = parser.parse_args()

    if args.video == '' and args.images == '' and  not args.http_server:
        raise ValueError('--video, --image or --http-server has to be provided ')

    if args.http_server:
        app.run(port = args.port, debug = True)
    else:
        frame_provider = ImageReader(args.images)
        if args.video != '':
            frame_provider = VideoReader(args.video)
        else:
            args.track = 0

        config(smooth = args.smooth, cpu = args.cpu)

        run_inference(frame_provider, args.height_size, args.track, args.no_display)

if __name__ == "__main__":
    main()