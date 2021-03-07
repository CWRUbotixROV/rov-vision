import cv2
import numpy as np
from vision import images
from matplotlib import pyplot as plt
import os

def draw_lines():

    img = cv2.imread("Capture.PNG")
    edges = cv2.Canny(img,100,200)

    plt.subplot(121),plt.imshow(img,cmap = 'gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(edges,cmap = 'gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

    plt.show()

"""
def draw_lines():
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=150, maxLineGap=100)

    if lines is not None:
        for i in range(len(lines)):
            line = lines[i]

            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

def detect_blue_poles(video):
    frame_num = 0
    count = 0

    images.clear_folder("transect", "frames")

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.color.COLOR_BGR2HSV)

        lower_bound_red = []
        upper_bound_red = []

        lower_bound_blue = []
        upper_bound_blue = []

        red_mask = cv2.inRange(hsv, lower_bound_red, upper_bound_red)
        blue_mask = cv2.inRange(hsv, lower_bound_blue, upper_bound_blue)

        lines = np.zeros_like(frame)
        draw_lines(frame, blue_mask)
"""
    # Get frame every few frames for image stitching
"""
        if count % 20 == 0:
            cv2.imwrite(get_folder("transect", "frames") + "/%d.jpg" % frame_num, frame)
            frame_num += 1
        count += 1
"""
        # Displaying the videos
        # cv2.imshow("lines", lines)
"""
        show_debug(frame, name="frame", wait=False)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
"""


    

