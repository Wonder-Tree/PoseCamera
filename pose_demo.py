import posecamera
import cv2

posecamera.load("./lightweight_pose_estimation.pth")

image = cv2.imread("tmp/boy.jpg")
poses = posecamera.estimate(image)
for pose in poses:
    pose.draw(image)

cv2.imshow("PoseCamera", image)
cv2.waitKey(0)