import cv2
import numpy as np
import os


def draw_lines(frame, mask):
    lines = cv2.HoughLinesP(mask, 1, np.pi/ 180, 100, minLineLength=40, maxLineGap=50)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


def clear_frames():
    for f in os.listdir("../vision/grid_map/frames"):
        os.remove(os.path.join("../vision/grid_map/frames", f))


def extract_frames(frame, count):
    cv2.imwrite("../vision/grid_map/frames/%d.jpg" % count, frame)


def image_stitching():
    file_names = []
    frames = []
    folder = os.listdir("../vision/grid_map/frames")

    for file in folder:
        file_names.append(file)

    file_names = sorted(file_names)

    for file in file_names:
        img = cv2.imread("../vision/grid_map/frames/" + file)
        img = cv2.resize(img, (0, 0), None, .6, 1)
        frames.append(img)

    stitcher = cv2.Stitcher.create()
    ret, final_image = stitcher.stitch(frames)

    if ret == cv2.STITCHER_OK:
        cv2.imshow("Final Image", final_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error during stitching")


def play_video(video):
    loop = 0  # For image stitching
    count = 0

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
        if loop % 50 == 0:
            extract_frames(frame, count)
            count += 1
        loop += 1

        # Displaying the videos
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

    # Stitch images in frames folder
    # image_stitching()
