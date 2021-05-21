# README

> _**NOTE:**_ Repository is still in development, please don't use for any production use.

## PoseCamera

[![PyPI version](https://badge.fury.io/py/posecamera.svg)](https://badge.fury.io/py/posecamera) [![PoseCamera Actions Status](https://github.com/Wonder-Tree/PoseCamera/workflows/build/badge.svg)](https://github.com/Wonder-Tree/PoseCamera/actions)  [![CodeFactor](https://www.codefactor.io/repository/github/wonder-tree/posecamera/badge)](https://www.codefactor.io/repository/github/wonder-tree/posecamera) [![](https://img.shields.io/badge/-Discussions-<COLOR>.svg)](https://github.com/Wonder-Tree/PoseCamera/discussions)

PoseCamera is python based SDK for multi human pose estimation through RGB webcam.

### Install

install posecamera package through pip

```python
pip install posecamera
```

If you are having issues with the installation on Windows OS then check this [page](https://usmankai.gitbook.io/posecamera-sdk/more-details/troubleshooting)

### Usage

draw pose keypoints on image

```python
import posecamera
import cv2

posecamera.load("__pretrained_wights_file_path")

image = cv2.imread("example.jpg")
poses = posecamera.estimate(image)
for pose in poses:
    pose.draw(image)

cv2.imshow("PoseCamera", image)
cv2.waitKey(0)
```

> Download Pretrained weights file from https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth

output of the above example

![](https://raw.githubusercontent.com/Wonder-Tree/PoseCamera/handtracking/tmp/output.png)

 

or get keypoints array

```text
for pose in poses:
    keypoints = pose.keypoints
```

output of handtracker (still in development)
![](https://raw.githubusercontent.com/Wonder-Tree/PoseCamera/handtracking/tmp/handtracker.png)

#### Using Docker

The official docker image is hosted on [Docker Hub](https://hub.docker.com/r/wondertree/posecamera). The very first step is to install the docker [docker](https://docs.docker.com/get-docker/) on your system.

> Also note that your Nvidia driver Needs to be compatible with CUDA10.2.

Doing inference on live webcam feed.

```bash
xhost +; docker run --name posecamera --rm --net=host --gpus all -e DISPLAY=$DISPLAY --device=/dev/video0:/dev/video0 wondertree/posecamera --video=0
```

> GPU & Webcam support \(if running docker\) is not available on Windows Operating System.

To run inference on images use the following command.

```bash
docker run --name posecamera --rm --net=host -e DISPLAY=$DISPLAY  wondertree/posecamera --images ./tmp/female_pose.jpg --cpu
```

For more details read our [Docs](https://usmankai.gitbook.io/posecamera-sdk/more-details)

The base of this repository is based on the following research paper.

```text
@inproceedings{osokin2018lightweight_openpose,
    author={Osokin, Daniil},
    title={Real-time 2D Multi-Person Pose Estimation on CPU: Lightweight OpenPose},
    booktitle = {arXiv preprint arXiv:1811.12004},
    year = {2018}
}
```

#### Share your thoughts

Join our [Discussion Channel](https://github.com/Wonder-Tree/PoseCamera/discussions)! We love to hear your ideas, suggestions or pull request

