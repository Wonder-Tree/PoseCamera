# Realtime inferencing 
The repository includes cli command ```posecamera``` file which expects several arguments which can be used to play different examples on videos and images.
```
posecamera --help
```
```
usage: posecamera [-h] [--checkpoint-path CHECKPOINT_PATH]
                   [--height-size HEIGHT_SIZE] [--video VIDEO]
                   [--images IMAGES [IMAGES ...]] [--cpu] [--track TRACK]
                   [--smooth SMOOTH] [--no-display] [--http-server]
                   [--port PORT]

optional arguments:
  -h, --help            show this help message and exit
  --checkpoint-path CHECKPOINT_PATH
                        path to the checkpoint
  --height-size HEIGHT_SIZE
                        network input layer height size
  --video VIDEO         path to video file or camera id
  --images IMAGES [IMAGES ...]
                        path to input image(s)
  --cpu                 run network inference on cpu
  --track TRACK         track pose id in video
  --smooth SMOOTH       smooth pose keypoints
  --no-display          hide gui
  --http-server         starts http server
  --port PORT           http server port

```

## Prediction on live webcam.
To predict human pose estimation from live webcam feed run the following example.
```
posecamera --video 0
```
Add ```--cpu``` argument if you don't have CUDA supported GPU.

## Inference on images
You have to pass --images argument and add images path separated by white space. If the path of your images has whitespace already then double-quote the path.
```
posecamera --images <path_to>/image_1.jpg <path_to>/image_2.jpg
```

## Use as REST API
You have to pass --http-server argument and --port = <port-number> , --port is optional but default value is 8080.
```
posecamera --http-server
```
then navigate to ```http://localost:8080``` on your browser and you will see some documentation to consume REST API.