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
    #cv2.imshow("blue", blue)
    #cv2.waitKey(0)
    
    # Find contours
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.drawContours(mask, contours, -1, (50,255,0), 3)
    resized = imutils.resize(img, width=300)
    cv2.imshow("contours", resized)
    cv2.waitKey(0)
    
    # Find max area contour
    maxc = 0
    for c in contours:
        if cv2.contourArea(c) > maxc:
            maxc = c
    
    # Find minimum bounding rectangle
    rect = cv2.minAreaRect(maxc)
    width = rect[1][0]
    height = rect[1][1]
    return (height/width)*1.85
    
print(measure_crack())