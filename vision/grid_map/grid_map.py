import cv2
import numpy as np


def test(cap):
    while cap.isOpened():
        _, frame = cap.read()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Lower and upper color bounds
        lower_red = np.array([150, 150, 150])
        upper_red = np.array([255, 255, 255])

        lower_blue = np.array([100, 200, 100])
        upper_blue = np.array([110, 255, 255])

        # Creating masks for red and blue
        r_mask = cv2.inRange(hsv, lower_red, upper_red)
        # r_result = cv2.bitwise_and(frame, frame, mask=r_mask)

        b_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # b_result = cv2.bitwise_and(frame, frame, mask=b_mask)

        # Using blue mask to find the two blue poles
        # edges = cv2.Canny(b_mask, 75, 150)
        lines = cv2.HoughLinesP(b_mask, 1, np.pi/180, 50, maxLineGap=50)

        # Drawing the lines
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

        # Displaying the videos
        cv2.imshow("frame", frame)
        # cv2.imshow("blue", b_mask)
        # cv2.imshow("Edges", edges)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
