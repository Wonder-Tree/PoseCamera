> **_NOTE:_**  Repository is still in development, please don't use for any production use.

# PoseCamera
[![PyPI version](https://badge.fury.io/py/posecamera.svg)](https://badge.fury.io/py/posecamera)
[![PoseCamera Actions Status](https://github.com/Wonder-Tree/PoseCamera/workflows/build/badge.svg)](https://github.com/Wonder-Tree/PoseCamera/actions)
<a href="https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth" title="PreTrainedModels"><img src="https://img.shields.io/badge/trained%20model-Download-brightgreen"></a>
[![CodeFactor](https://www.codefactor.io/repository/github/wonder-tree/posecamera/badge)](https://www.codefactor.io/repository/github/wonder-tree/posecamera)
[![](https://img.shields.io/badge/-Discussions-<COLOR>.svg)](https://github.com/Wonder-Tree/PoseCamera/discussions)

PoseCamera is python based SDK for multi human pose estimation through RGB webcam.

## Install
install posecamera package through pip
```
pip install posecamera
```

If you are having issues with the installation on Windows OS then check this [page](https://wonder-tree.github.io/PoseCamera/#/pages/troubleshooting)

## Usage

draw pose keypoints on image
```
import posecamera
import cv2

image = cv2.imread("example.jpg")
poses = posecamera.estimate(image)
for pose in poses:
    pose.draw(image)

cv2.imshow("PoseCamera", image)
cv2.waitKey(0)
```

> Above example will automatically download the pretrained model. If you want to train your own model visit [Train your own model](https://wonder-tree.github.io/PoseCamera/#/pages/training?id=training-on-your-own-data)

output of above example
![PoseCamera example output](https://github.com/Wonder-Tree/PoseCamera/blob/master/tmp/output.png?raw=true)

or get keypoints array
```
for pose in poses:
    keypoints = pose.keypoints
```

### Using Docker
The official docker image is hosted on [Docker Hub](https://hub.docker.com/r/wondertree/posecamera). The very first step is to install the docker [docker](https://docs.docker.com/get-docker/) on your system. 
> Also note that your Nvidia driver Needs to be compatible with CUDA10.2.

Doing inference on live webcam feed.
```sh
xhost +; docker run --name posecamera --rm --net=host --gpus all -e DISPLAY=$DISPLAY --device=/dev/video0:/dev/video0 wondertree/posecamera --video=0
```
> GPU & Webcam support (if running docker) is not available on Windows Operating System. 

To run inference on images use following command.
```sh
docker run --name posecamera --rm --net=host -e DISPLAY=$DISPLAY  wondertree/posecamera --images ./tmp/female_pose.jpg --cpu
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

### Share your thoughts
Join our [Discussion Channel](https://github.com/Wonder-Tree/PoseCamera/discussions)! We love to hear your ideas, suggestions or pull request
