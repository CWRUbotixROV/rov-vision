import cv2
import numpy as np
import os


def draw_lines(frame, mask):
    lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=40, maxLineGap=50)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


def clear_frames():
    for f in os.listdir("../vision/grid_map/frames"):
        os.remove(os.path.join("../vision/grid_map/frames", f))


def extract_frames(frame, count):
    cv2.imwrite("../vision/grid_map/frames/frame%d.jpg" % count, frame)


def play_video(video):
    count = 0  # For image stitching

    # Clear frames folder
    clear_frames()

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Lower and upper color bounds
        lower_red = np.array([150, 150, 150])
        upper_red = np.array([255, 255, 255])

        lower_blue = np.array([100, 200, 100])
        upper_blue = np.array([110, 255, 255])

        # Creating masks for red and blue
        r_mask = cv2.inRange(hsv, lower_red, upper_red)  # Red
        b_mask = cv2.inRange(hsv, lower_blue, upper_blue)  # Blue

        # Draw lines onto the original video
        draw_lines(frame, b_mask)

        # Get frames for image stitching
        extract_frames(frame, count)
        count += 1

        # Displaying the videos
        cv2.imshow("frame", frame)
        # cv2.imshow("blue", b_mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
