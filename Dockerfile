FROM ubuntu:latest

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

# Install Dependencies
RUN cd /PoseCamera && pip install -r requirements.txt

# Setup PYTHONPATH
RUN export PYTHONPATH=$PYTHONPATH:/PoseCamera

# Build Package
WORKDIR /PoseCamera
RUN pip install setuptools wheel && pip install .

# Run app
ENTRYPOINT ["posecamera"]