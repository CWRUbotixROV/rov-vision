import cv2, imutils
import numpy as np

def measure_crack():
    image = cv2.imread('crack3.jpg', cv2.IMREAD_COLOR)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([90,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Bitwise-AND mask and original image
    #blue = cv2.bitwise_and(image, image, mask= mask)
    
    #cv2.imshow("mask", mask)
    #cv2.waitKey(0)
    
    # Find contours
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.drawContours(mask, contours, -1, (50,255,0), 3)
    resized = imutils.resize(img, width=300)
    cv2.imshow("contours", resized)
    cv2.waitKey(0)
    
    # Find max area contour
    maxArea = 0
    
    for c in contours:
        if cv2.contourArea(c) > maxArea:
            maxArea = cv2.contourArea(c)
            maxc = c
    
    # Find minimum bounding rectangle
    rect = cv2.minAreaRect(maxc)
    width = rect[1][0]
    height = rect[1][1]
    if height > width:
        return (height/width)*1.85
    else:
    	return (width/height)*1.85

def measure_crack2():
    image = cv2.imread('crack3.jpg', cv2.IMREAD_COLOR)
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower = np.array([0,0,0])
    upper = np.array([180,50,100])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower, upper)
    
    resized = imutils.resize(mask, width=300)
    cv2.imshow("mask", resized)
    cv2.waitKey(0)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)

    # Here we use an adaptive threshold on the image, since we expect the lighting to be non-uniform.
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 0)
    resized = imutils.resize(thresh, width=300)
    #cv2.imshow("thresh", resized)
    #cv2.waitKey(0)
    
    # Canny line detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    resized = imutils.resize(edges, width=300)
    cv2.imshow("edges", resized)
    cv2.waitKey(0)
    
    lines = cv2.HoughLines(mask, 1, np.pi/180, 500)
    a,b,c = lines.shape
    for i in range(a):
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 10000*(-b))
        y1 = int(y0 + 10000*(a))
        x2 = int(x0 - 10000*(-b))
        y2 = int(y0 - 10000*(a))
        #print(str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2))
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
    
    resized = imutils.resize(image, width=300)
    cv2.imshow("lines", resized)
    cv2.waitKey(0)
    
    # Find contours
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.drawContours(image, contours, -1, (50,255,0), 3)
    resized = imutils.resize(img, width=300)
    #cv2.imshow("contours", resized)
    #cv2.waitKey(0)
    
    return 0

print(measure_crack2())