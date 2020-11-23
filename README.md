> **_NOTE:_**  Repository is still in development, please don't use for any production use.

# PoseCamera
[![PoseCamera Actions Status](https://github.com/Wonder-Tree/PoseCamera/workflows/build/badge.svg)](https://github.com/Wonder-Tree/PoseCamera/actions)
<a href="https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth" title="PreTrainedModels"><img src="https://img.shields.io/badge/trained%20model-Download-brightgreen"></a>
[![CodeFactor](https://www.codefactor.io/repository/github/wonder-tree/posecamera/badge)](https://www.codefactor.io/repository/github/wonder-tree/posecamera)

PoseCamera is python based SDK for multi human pose estimation through RGB webcam.

## Installation
install posecamera package thorugh ***pip***
`pip install posecamera`
If you are installation on Windows OS please see some [troubleshoots](https://wonder-tree.github.io/PoseCamera/#/pages/troubleshooting) 

## Usage

draw pose keypoints on image
```
import posecamera
import cv2

image = cv2.imread("./tmp/female_pose.jpg")
poses = posecamera.estimate(image)
for pose in poses:
    pose.draw(image)

cv2.imshow("PoseCamera", image)
cv2.waitKey(0)
```

output of above example
![PoseCamera example output](https://github.com/Wonder-Tree/PoseCamera/blob/testing/output.png?raw=true)

or get keypoints array
```
for pose in poses:
    keypoints = pose.keypoints
```

### Using Docker
The official docker image is hosted on [Docker Hub](https://hub.docker.com/r/wondertree/posecamera). The very first step is to install the docker [docker](https://docs.docker.com/get-docker/) on your system. You can also use ```pose-cli.py``` locally with installing all dependencies listed in ```requirements.txt```. 
> Also note that your Nvidia driver Needs to be compatible with CUDA10.2.

Doing inference on live webcam feed.
```sh
xhost +; docker run --name posecamera --rm --gpus all -e DISPLAY=$DISPLAY --device=/dev/video0:/dev/video0 wondertree/posecamera --video=0
```
> GPU & Webcam support (if running docker) is not available on Windows Operating System. 

To run inference on images use following command.
```sh
docker run --name posecamera --rm -e DISPLAY=$DISPLAY  wondertree/posecamera --images ./tmp/female_pose.jpg --cpu
```

For more details read our [Docs](https://wonder-tree.github.io/PoseCamera)

The base of this repository is based on the following research paper.
```
@inproceedings{osokin2018lightweight_openpose,
    author={Osokin, Daniil},
    title={Real-time 2D Multi-Person Pose Estimation on CPU: Lightweight OpenPose},
    booktitle = {arXiv preprint arXiv:1811.12004},
    year = {2018}
}
```