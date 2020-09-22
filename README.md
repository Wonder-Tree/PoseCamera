> **_NOTE:_**  Repository is still in development, Please don't use for any production use.

# PoseCamera
[![PoseCamera Actions Status](https://github.com/Wonder-Tree/PoseCamera/workflows/build/badge.svg)](https://github.com/Wonder-Tree/PoseCamera/actions)
<a href="https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth" title="PreTrainedModels"><img src="https://img.shields.io/badge/trained%20model-Download-brightgreen"></a>

PoseCamera is Socket based sdk for multi human pose estimation through rgb webcam. You can integrate this sdk into any programming language. 

### Quick Start
The official docker image is hosted on [Docker Hub](https://hub.docker.com/r/wondertree/posecamera). You must have installed [docker](https://docs.docker.com/get-docker/) on your system. You can also use ```pose-cli.py``` localy with installing all dependencies listed in ```requirements.txt```. 
> Also note that your nvidia driver should be compatible with CUDA10.2.

Doing inference on live webcam feed.
```sh
xhost +; docker run --name posecamera --rm --gpus all -e DISPLAY=$DISPLAY --device=/dev/video0:/dev/video0 wondertree/posecamera --video=0
```
> GPU & Webcam support (if running docker) is not available on Windows Operating System. 

To run inference on images use following command.
```sh
docker run --name posecamera --rm -e DISPLAY=$DISPLAY  wondertree/posecamera --images ./demo/female_pose.jpg --cpu
```
The base of this repository is based on following research paper.
```
@inproceedings{osokin2018lightweight_openpose,
    author={Osokin, Daniil},
    title={Real-time 2D Multi-Person Pose Estimation on CPU: Lightweight OpenPose},
    booktitle = {arXiv preprint arXiv:1811.12004},
    year = {2018}
}
```