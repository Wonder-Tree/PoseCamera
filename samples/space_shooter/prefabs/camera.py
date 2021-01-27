import cv2
import numpy as np
import config
import pygame
import posecamera

class Camera(object):
    def __init__(self) -> None:
        super().__init__()

        self.capture = cv2.VideoCapture(0)
    
    def read(self):
        _, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize frame 
        # according to screen
        frame = cv2.resize(frame, (config.WIDTH, config.HEIGHT))

        # Draw pose
        self.poses = posecamera.estimate(frame)
        for pose in self.poses:
            pose.draw(frame)

        # and fix rotation
        frame = np.fliplr(frame)
        frame = np.rot90(frame)

        # Convert frame into pygame surface
        return pygame.surfarray.make_surface(frame)
    