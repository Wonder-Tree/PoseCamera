import posecamera
import cv2

det = posecamera.pose_tracker.PoseTracker()

image = cv2.imread("tmp/boy.jpg")
pose = det(image)

for name, (y, x, score) in pose.keypoints.items():
    cv2.circle(image, (int(x), int(y)), 4, (255, 0, 0), -1)

cv2.imshow("PoseCamera - Pose Tracking", image)
cv2.waitKey(0)