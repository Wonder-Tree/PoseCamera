#FROM nvidia/cuda:10.2-devel-ubuntu18.04
FROM anibali/pytorch:1.5.0-cuda10.2

USER root

# Install Packages
RUN apt-get update 

RUN apt-get install -y wget build-essential cmake git unzip 

RUN apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libgtk-3-dev 

# Clone PoseCamera repo
COPY . /PoseCamera

RUN pip install --upgrade pip

# Install cython
RUN pip install cython numpy scikit-build opencv-python

RUN pip install pycocotools==2.0.0 --ignore-installed

# Install Dependencies
RUN cd /PoseCamera && pip install -r requirements.txt

# Download pre-trained model file
RUN curl -o /PoseCamera/checkpoint_iter_50000.pth https://storage.googleapis.com/wt_storage/checkpoint_iter_50000.pth

# Run app
WORKDIR /PoseCamera
ENTRYPOINT ["python", "pose-cli.py"]