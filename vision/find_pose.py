import numpy as np
from numpy.linalg import norm
import cv2

def two_largest(contours):
    tl = contours[0:2]
    for cn in contours[2:]:
        if cn.contourArea > tl[0].contourArea:
            tl[0] = cn
        elif cn.contourArea > tl[1].contourArea:
            tl[1] = cn
    return tl

def angle_between(v1, v2):
    return np.arccos(np.clip(np.dot(v1, v2)/norm(v1)/norm(v2), -1, 1))

# Returns a vector normal to the line connecting the centroids of the two contours, pointing forward.
def normal_line(contours):
    m1 = cv2.moments(contours[0])
    m2 = cv2.moments(contours[1])
    c1 = np.array([m1['m10']/m1['m00'], m1['m01']/m1['m00']])
    c2 = np.array([m2['m10']/m2['m00'], m2['m01']/m2['m00']])
    # print(c1, c2)
    vec = c2 - c1
    # print(vec)
    return np.array([vec[1]/vec[0], -1])    # force vector to point forward (negative y)


def find_angle(frame):
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blurred = cv2.GaussianBlur(frame, (5,5), 0)

    # replace with Ryan's thing later
    lower_red = np.array([0, 0, 254])
    upper_red = np.array([80, 80, 255])
    lower_blue = np.array([254, 0, 0])
    upper_blue = np.array([255, 1, 1])
    # print(blurred)

    r_mask = cv2.inRange(blurred, lower_red, upper_red)
    b_mask = cv2.inRange(blurred, lower_blue, upper_blue)
    contours_r, _ = cv2.findContours(r_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_b, _ = cv2.findContours(b_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print(contours_r)
    two_largest_r = two_largest(contours_r)
    two_largest_b = two_largest(contours_b)
    # print(two_largest_r)
    nl = normal_line(two_largest_r)
    print(nl)
    print("Angle from forward: {}".format(-angle_between(np.array([0,-1]), nl)))

    cv2.imshow('Red mask', r_mask)
    cv2.waitKey(0)

    # r_edged = cv2.Canny()
    # contours, _ = cv2.findContours

find_angle(cv2.imread('test_transect.png'))
