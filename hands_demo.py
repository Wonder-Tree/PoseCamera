import posecamera
import cv2
det = posecamera.hand_tracker.HandTracker("palm_detection_without_custom_op.tflite", "hand_landmark.tflite", "anchors.csv")

image = cv2.imread("tmp/hands.jpg")
keypoints, bbox = det(image)

for hand_keypoints in keypoints:
    for (x, y) in hand_keypoints:
        cv2.circle(image, (int(x), int(y)), 3, (255, 0, 0), -1)

cv2.imshow("PoseCamera - Hand Tracking", image)
cv2.waitKey(0)