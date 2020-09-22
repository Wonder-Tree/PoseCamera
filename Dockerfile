#FROM nvidia/cuda:10.2-devel-ubuntu18.04
FROM vastai/pytorch

USER root

# Install Non-GPU Dependencies.
RUN apt-get update && apt-get install -y build-essential cmake git 

# Install OpenCV Dependencies
RUN apt-get install -y \
    libopencv-dev

# Clone PoseCamera repo
COPY . /PoseCamera

# Install cython
RUN pip install cython numpy scikit-build

# Due to some opencv installation issue we have to downgrade pip version
RUN pip install --upgrade --force-reinstall pip==9.0.3

# Install Dependencies
RUN cd /PoseCamera && pip install -r requirements.txt

# Download pre-trained model file
RUN curl -o /PoseCamera/checkpoint_iter_50000.pth https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth

# Nvidia drivers
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:graphics-drivers 
RUN apt install nvidia-driver-440 -y

# Run app
WORKDIR /PoseCamera
ENTRYPOINT ["python", "pose-cli.py"]