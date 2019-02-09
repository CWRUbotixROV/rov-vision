import cv2, imutils
import numpy as np

def measure_crack():
    image = cv2.imread('crack.png', cv2.IMREAD_COLOR)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([90,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Bitwise-AND mask and original image
    blue = cv2.bitwise_and(image, image, mask= mask)
    
    cv2.imshow("mask", mask)
    cv2.waitKey(0)
    cv2.imshow("blue", blue)
    cv2.waitKey(0)
    
measure_crack()