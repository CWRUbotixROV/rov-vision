import cv2, imutils
import numpy as np
import math
import colors

def measureCrackRatio(image):
    """ Measures crack using raio method"""

    CRACK_WIDTH = 1.9

    #Get dimensions of blue rectangle
    width, height = blueRectangle(image)
    
    # Return larger dimension. Multiply ratio by CRACK_WIDTH
    if height > width:
        return (height/width) * CRACK_WIDTH
    else:
        return (width/height) * CRACK_WIDTH
	
def blueRectangle(image):
    """Finds dimensions of a blue rectangle"""
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    LOWER_BLUE = colors.LOWER_BLUE
    UPPER_BLUE = colors.UPPER_BLUE

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(image, LOWER_BLUE, UPPER_BLUE)
    cv2.imshow("mask", mask)
    cv2.waitKey(0)
    
    # Find contours
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find max area contour
    maxContour = contours[0]
    
    for c in contours:
        if cv2.contourArea(c) > cv2.contourArea(maxContour):
            maxContour = c
    
    # Find minimum bounding rectangle
    rect = cv2.minAreaRect(maxContour)
    width = rect[1][0]
    height = rect[1][1]
    return width, height

def measureCrackPerspective(image):
    """Measures crack using perspective transformation method"""
    # define range of color for black grid lines in HSV
    LOWER_BLACK = np.array([0,0,0])
    UPPER_BLACK = np.array([180,50,100])

    # Gaussian Blur
    KERNEL_SIZE = (5, 5)
    blurredcolor = cv2.GaussianBlur(image, KERNEL_SIZE, 0)
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blurredcolor, cv2.COLOR_BGR2HSV)
    
    # Threshold the HSV image to get only black colors
    mask = cv2.inRange(hsv, LOWER_BLACK, UPPER_BLACK)
    
    # Detect lines
    LINE_THRESH = 700
    lines = cv2.HoughLines(mask, 1, np.pi/180, LINE_THRESH)
    # If no lines are detected, revert to ratio method
    if (lines is None):
        return measureCrackRatio(image)
    a,b,c = lines.shape
    
    top = []
    bottom = []
    left = []
    right = []
    
    height, width, channels = image.shape

    ANGLE_THRESH = 0.2
    PARTITION = 0.25
    
    for i in range(a):
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        
        # Sort lines into left, right, top, and bottom
        if (theta < ANGLE_THRESH):
            if (rho < PARTITION * width):
                left.append([rho, theta])
            elif (rho > (1 - PARTITION) * width):
                right.append([rho, theta])
        elif (theta > math.pi - ANGLE_THRESH):
            if (rho > -PARTITION * width):
                left.append([rho, theta])
            elif (rho < -(1 - PARTITION) * width):
                right.append([rho, theta])
        elif (theta > (math.pi / 2 - ANGLE_THRESH) and theta < (math.pi / 2 + ANGLE_THRESH)):
            if (rho < PARTITION * height):
                top.append([rho, theta])
            elif (rho > (1 - PARTITION) * height):
                bottom.append([rho, theta])
    
    # If grid line detection fails, revert to ratio method
    if (len(top) == 0 or len(bottom) == 0 or len(left) == 0 or len(right) == 0):
        return measureCrackRatio(image)

    x1, y1 = intersect(top, left)
    x2, y2 = intersect(top, right)
    x3, y3 = intersect(bottom, left)
    x4, y4 = intersect(bottom, right)
    
    IMAGE_SIZE = 3000
    # Find number of cm per pixel
    SCALE = 30 / IMAGE_SIZE

    # Find perspective transform matrix
    src = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    dst = np.float32([[0, 0], [IMAGE_SIZE, 0], [0, IMAGE_SIZE], [IMAGE_SIZE, IMAGE_SIZE]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    
    # Perspective transform original image
    warped = cv2.warpPerspective(image, matrix, (IMAGE_SIZE, IMAGE_SIZE))
    
    width, height = blueRectangle(warped)
    
    # Find larger dimension and scale it into cm
    if (width > height):
        ret = width * SCALE
    else:
        ret = height * SCALE
    
    # If dimension is out of bounds, revert to ratio method
    if (ret > 21 or ret < 7):
        return measureCrackRatio(image)
    else:
        return ret
   
def intersect(lines1, lines2):
    """Find the average intersection point between two sets of lines"""
    xcoords = []
    ycoords = []
    for line1 in lines1:
        slope1, yint1 = convertToSlopeInt(line1)
        for line2 in lines2:
            # Change vertical line to slightly off vertical to avoid divide by 0 errors
            if (line2[1] == 0.0):
                line2[1] = 0.0001
            slope2, yint2 = convertToSlopeInt(line2)
            x = (yint1 - yint2) / (slope2 - slope1)
            y = slope1 * x + yint1
            xcoords.append(x)
            ycoords.append(y)
    meanx = int(sum(xcoords) / len(xcoords))
    meany = int(sum(ycoords) / len(ycoords))
    return meanx, meany

def convertToSlopeInt(line):
    """Converts a line into slope intercept form"""
    rho = line[0]
    theta = line[1]
    cos = np.cos(theta)
    sin = np.sin(theta)
    slope = -cos / sin
    x = cos * rho
    y = sin * rho
    yint = y - (x * slope)
    return slope, yint

image = cv2.imread("pictures-6-10/capture6.PNG")
print(measureCrackPerspective(image))