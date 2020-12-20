from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from vision.images import *
import utils
import cv2
import numpy as np


def draw_lines(frame, mask):
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=40, maxLineGap=50)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


def clear_frames():
    clear_folder("transect", "frames")


def get_frames(frame, count):
    cv2.imwrite(get_folder("transect", "frames") + "/%d.jpg" % count, frame)


def image_stitching():
    frames = []

    frames = get_all_images("transect", "frames")

    stitcher = cv2.Stitcher.create()
    ret, final_image = stitcher.stitch(frames)

    if ret == cv2.STITCHER_OK:
        cv2.imshow("Final Image", final_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error during stitching")


def centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins = numLabels)
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
    # return the histogram
    return hist


def plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0
    # loop over the percentage of each cluster and the color of
    # each cluster
    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart
    return bar


def test(video, clusters):
    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        vid = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vid = vid.reshape((frame.shape[0] * frame.shape[1], 3))

        clt = KMeans(n_clusters=clusters)
        clt.fit(vid)

        hist = centroid_histogram(clt)
        bar = plot_colors(hist, clt.cluster_centers_)

        cv2.imshow("frame", frame)
        cv2.imshow("bar", bar)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()


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
            get_frames(frame, count)
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
