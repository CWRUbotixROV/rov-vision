"""Contains methods to map video with lines from a mask"""

from vision.images import *
import cv2
import numpy as np
import time

def clear_frames():
    """Clears the folder
    No arguments"""
    clear_folder("transect", "frames")


def get_frame(frame, count):
    cv2.imwrite(get_folder("transect", "frames") + "/%d.jpg" % count, frame)


def image_stitching():
    """Stitches images together
    No arguments"""
    print("Starting image stitching")

    frames = get_all_images("transect", "frames")

    stitcher = cv2.Stitcher.create(mode=cv2.STITCHER_SCANS)
    ret, stitched_img = stitcher.stitch(frames)

    if ret == cv2.STITCHER_OK:
        stitched_img = cv2.resize(stitched_img, (0, 0), None, .5, .5)
        cv2.imshow("Final Image", stitched_img)

        cv2.imwrite(get_folder("transect") + "/stitched_img.jpg", stitched_img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        print("Error during stitching")


def draw_lines(frame, mask):
    """Draws HoughLines on image
    For example: 'draw_lines(frame, edges)'"""
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=100, maxLineGap=100)

    if lines is not None:
        for i in range(len(lines)):
            line = lines[i]

            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


def empty(a):
    pass


def find_squares(mask, frame, squares, num):
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    found = False  # If square was found

    for cnt in contours:
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, .01 * cv2.arcLength(cnt, True), True)

        if area > 10000:
            # cv2.drawContours(frame, [approx], 0, (255, 0, 0), 5)

            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w)/h

                # Check if sides are equal-ish lengths
                if .5 <= aspect_ratio <= 1.5:
                    cv2.putText(frame, str(num), (x + int(w / 2), y + int(w / 2)), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0))
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
                    found = True

        if found:
            num += 1
            found = False

    return num


def start_mapping(video):

    cv2.namedWindow("Trackbar")
    cv2.createTrackbar("Thresh1", "Trackbar", 87, 255, empty)
    cv2.createTrackbar("Thresh2", "Trackbar", 230, 255, empty)

    squares = []  # Tracks square objects
    num = 0  # Unique ID for each square

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        blur = cv2.GaussianBlur(frame, (7, 7), 1)

        thresh1 = cv2.getTrackbarPos("Thresh1", "Trackbar")
        thresh2 = cv2.getTrackbarPos("Thresh2", "Trackbar")

        canny = cv2.Canny(blur, thresh1, thresh2)

        lines = np.zeros_like(frame)
        draw_lines(lines, canny)

        kernel = np.ones((5, 5))
        lines = cv2.dilate(lines, kernel, iterations=1)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        num = find_squares(lines, frame, squares, num)

        cv2.imshow("frame", frame)
        # cv2.imshow("canny", canny)
        # cv2.imshow("lines", lines)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


def find_blue_poles(video):
    """Maps video and displays video with lines drawn on
    For example: 'start_mapping("get_video("transect", "transect.MOV")")'"""
    frame_num = 0  # For naming frames
    current_time = time.time()

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

        # Draw lines where blue poles are
        lines = np.zeros_like(frame)
        draw_lines(lines, b_mask)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        contours = np.zeros_like(frame)
        get_contours(lines, contours)

        # Get frame every .5 seconds for image stitching
        # if time.time() - current_time >= .5:
        #     get_frame(frame, frame_num)
        #     current_time = time.time()
        #     frame_num += 1

        # Displaying the videos
        cv2.imshow("lines", lines)
        cv2.imshow("contours", contours)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
