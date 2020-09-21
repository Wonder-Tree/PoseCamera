FROM nvidia/cuda:10.2-devel-ubuntu18.04

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    git \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Non-GPU Dependencies.
RUN apt update --allow-unauthenticated && version="7.0.0-1+cuda10.2" ; \
    apt install -y \
    libnvinfer7=${version} libnvonnxparsers7=${version} libnvparsers7=${version} \
    libnvinfer-plugin7=${version} libnvinfer-dev=${version} libnvonnxparsers-dev=${version} \
    libnvparsers-dev=${version} libnvinfer-plugin-dev=${version} python-libnvinfer=${version} \
    python3-libnvinfer=${version} && \
    apt-mark hold \
    libnvinfer7 libnvonnxparsers7 libnvparsers7 libnvinfer-plugin7 libnvinfer-dev libnvonnxparsers-dev libnvparsers-dev libnvinfer-plugin-dev python-libnvinfer python3-libnvinfer

# Install OpenCV Dependencies
RUN apt install -y software-properties-common || apt install -y software-properties-common && \
    add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main" && \
    APT_DEPS="git cmake libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev x264 v4l-utils python3-dev python3-pip libcanberra-gtk-module libcanberra-gtk3-module" && \
    apt install -y $APT_DEPS || apt install -y $APT_DEPS

# Clone PoseCamera repo
COPY . /PoseCamera

# Install cython
RUN pip3 install cython

# Install Dependencies
RUN cd ./PoseCamera && pip3 install -r requirements.txt

# Download pre-trained model file
RUN curl -o ./PoseCamera/checkpoint_iter_50000.pth https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth

# Run app
WORKDIR ./PoseCamera
CMD python pose-cli.py --checkpoint-path ./checkpoint_iter_50000.pth --images ./demo