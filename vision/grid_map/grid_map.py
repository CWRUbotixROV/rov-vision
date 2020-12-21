from vision.images import *
import cv2
import numpy as np
import time


def draw_lines(frame, mask):
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=40, maxLineGap=50)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


def clear_frames():
    clear_folder("transect", "frames")


def get_frame(frame, count):
    cv2.imwrite(get_folder("transect", "frames") + "/%d.jpg" % count, frame)


def image_stitching():
    print("Starting image stitching")

    frames = get_all_images("transect", "frames")

    stitcher = cv2.Stitcher.create(mode=cv2.STITCHER_SCANS)
    ret, final_image = stitcher.stitch(frames)

    if ret == cv2.STITCHER_OK:
        final_image = cv2.resize(final_image, (0, 0), None, .5, .5)
        cv2.imshow("Final Image", final_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error during stitching")


def start_mapping(video):
    count = 0
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

        # Draw lines onto the original video
        draw_lines(frame, b_mask)

        # Get frame every 1 second for image stitching
        if time.time() - current_time >= 1:
            get_frame(frame, count)
            current_time = time.time()
            count += 1

        # Displaying the videos
        cv2.imshow("frame", frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

    # Stitch images in frames folder
    image_stitching()
