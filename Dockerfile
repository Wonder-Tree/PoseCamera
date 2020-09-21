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

# Create a working directory
RUN mkdir /app
WORKDIR /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN chmod 777 /home/user

# Install Miniconda and Python 3.6
ENV CONDA_AUTO_UPDATE_CONDA=false
ENV PATH=/home/user/miniconda/bin:$PATH
RUN curl -sLo ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh \
 && conda install -y python==3.6.9 \
 && conda clean -ya

# Install OpenCV Dependencies
RUN apt install -y software-properties-common || apt install -y software-properties-common && \
    add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main" && \
    APT_DEPS="git cmake libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev x264 v4l-utils python3-dev python3-pip libcanberra-gtk-module libcanberra-gtk3-module" && \
    apt install -y $APT_DEPS || apt install -y $APT_DEPS
    
# CUDA 10.1-specific steps
RUN conda install -y -c pytorch \
    cudatoolkit=10.1 \
    "pytorch=1.4.0=py3.6_cuda10.1.243_cudnn7.6.3_0" \
    "torchvision=0.5.0=py36_cu101" \
 && conda clean -ya

# Clone PoseCamera repo
RUN git clone https://github.com/Wonder-Tree/PoseCamera.git
RUN pip install --upgrade cython
RUN cd ./PoseCamera && pip install -r requirements.txt

#RUN sudo apt update && sudo apt install -y libgl1-mesa-glx
#RUN sudo apt install -y libgtk2.0-dev

# Download pre-trained model file
RUN curl -o ./PoseCamera/checkpoint_iter_50000.pth https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth

# Run app
WORKDIR ./PoseCamera
CMD python pose-cli.py --checkpoint-path ./checkpoint_iter_50000.pth --images ./demo