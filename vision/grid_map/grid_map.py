"""Contains methods to map video with lines from a mask"""

from vision.images import *
import cv2
import numpy as np


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
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=150, maxLineGap=100)

    if lines is not None:
        for i in range(len(lines)):
            line = lines[i]

            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


class Square:
    def __init__(self, num, x, y, w, h, visible):
        self.num = num
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.visible = visible
        self.delete = 20


def find_squares(mask, frame):
    global num
    global squares
    curr_squares = []  # Squares in the current frame

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
                    curr_squares.append(Square(-1, x, y, w, h, True))

    if len(squares) == 0:
        for s in curr_squares:
            num += 1
            s.num = num
            squares.append(s)

    elif len(curr_squares) >= len(squares):
        matched = []

        for s1 in curr_squares:
            for s2 in squares:
                if np.allclose([s1.x, s1.y, s1.w, s1.h], [s2.x, s2.y, s2.w, s2.h], atol=50):
                    s2.x = s1.x
                    s2.y = s1.y
                    s2.w = s1.w
                    s2.h = s1.h

                    s1.num = s2.num
                    matched.append(s1.num)

                    s2.delete = 20

        if len(curr_squares) != len(matched):
            for s in curr_squares:
                if s.num not in matched:
                    num += 1
                    s.num = num
                    matched.append(s.num)
                    squares.append(s)

    else:
        matched = []

        for s in curr_squares:
            s.visible = False

        for s in squares:
            s.visible = False

        for s1 in curr_squares:
            for s2 in squares:
                if np.allclose([s1.x, s1.y, s1.w, s1.h], [s2.x, s2.y, s2.w, s2.h], atol=50):
                    s2.x = s1.x
                    s2.y = s1.y
                    s2.w = s1.w
                    s2.h = s1.h

                    s1.num = s2.num
                    matched.append(s1.num)

                    s2.visible = True
                    s2.delete = 20
                    break

        if len(curr_squares) != len(matched):
            for s in curr_squares:
                if s.num not in matched:
                    num += 1
                    s.num = num
                    matched.append(s.num)
                    squares.append(s)

        for s in squares:
            if not s.visible:
                if s.delete == 0:
                    squares.remove(s)
                else:
                    s.delete -= 1

    for s in squares:
        if s.visible:
            cv2.putText(frame, str(s.num), (s.x + int(s.w / 2), s.y + int(s.w / 2)),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0))
            cv2.rectangle(frame, (s.x, s.y), (s.x + s.w, s.y + s.h), (0, 255, 0), 5)


# Used for trackbar
def empty(a):
    pass


squares = []  # Tracks square objects
num = 0  # Unique ID for each square


def start_mapping(video):

    cv2.namedWindow("Trackbar")
    cv2.createTrackbar("Thresh1", "Trackbar", 87, 255, empty)
    cv2.createTrackbar("Thresh2", "Trackbar", 230, 255, empty)

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

        kernel = np.ones((10, 10))
        lines = cv2.dilate(lines, kernel, iterations=1)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        find_squares(lines, frame)

        cv2.imshow("frame", frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


def find_blue_poles(video):
    """Detects where the two blue poles are
    For example: 'start_mapping("get_video("transect", "transect.MOV")")'"""
    frame_num = 0  # For naming frames
    count = 0 #  Tracks frame count

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
        draw_lines(frame, b_mask)

        # Get frame every few frames for image stitching
        if count % 20 == 0:
            get_frame(frame, frame_num)
            frame_num += 1
        count += 1

        # Displaying the videos
        # cv2.imshow("lines", lines)
        cv2.imshow("frame", frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
