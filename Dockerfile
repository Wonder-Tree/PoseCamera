#FROM nvidia/cuda:10.2-devel-ubuntu18.04
FROM anibali/pytorch:1.5.0-cuda10.2

USER root

# Install Packages
RUN apt-get update && apt-get install -y --no-install-recommends python \
 wget build-essential cmake git unzip \
 libavcodec-dev libavformat-dev libswscale-dev libgtk-3-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
 
# Clone PoseCamera repo
COPY . /PoseCamera

RUN pip install --upgrade pip

# Install cython
RUN pip install cython numpy scikit-build opencv-python

RUN pip install pycocotools==2.0.0 --ignore-installed

# Install Dependencies
RUN cd /PoseCamera && pip install -r requirements.txt

# Setup PYTHONPATH
RUN export PYTHONPATH=$PYTHONPATH:/PoseCamera

# Build Package
WORKDIR /PoseCamera
RUN pip install setuptools wheel && pip install .

# Run app
ENTRYPOINT ["posecamera"]