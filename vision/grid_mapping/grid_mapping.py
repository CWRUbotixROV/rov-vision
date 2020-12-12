import cv2
import numpy as np

cap = cv2.VideoCapture("../vision/grid_mapping/transect.MOV")

while cap.isOpened():
    _, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([150, 150, 150])
    upper_red = np.array([255, 255, 255])

    lower_blue = np.array([100, 200, 100])
    upper_blue = np.array([110, 255, 255])

    r_mask = cv2.inRange(hsv, lower_red, upper_red)
    r_result = cv2.bitwise_and(frame, frame, mask=r_mask)

    b_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    b_result = cv2.bitwise_and(frame, frame, mask=b_mask)

    cv2.imshow("frame", frame)
    cv2.imshow("red", r_result)
    cv2.imshow("blue", b_result)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
