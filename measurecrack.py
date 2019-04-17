import cv2, imutils
import numpy as np

# Measures crack using raio method
def measure_crack(image):
    # Get dimensions of blue rectangle
    width, height = blue_rectangle(image)
    
    # Return larger dimension. Multiply ratio by 1.85
    if height > width:
        return (height/width)*1.9
    else:
        return (width/height)*1.9

# Finds dimensions of a blue rectangle    	
def blue_rectangle(image):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([90,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Find contours
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.drawContours(mask, contours, -1, (50,255,0), 3)
    
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
    return width, height

# Measures crack using perspective transformation method
def measure_crack2(image):
    # define range of color in HSV
    lower = np.array([0,0,0])
    upper = np.array([180,50,100])

    #Gaussian Blur
    blurredcolor = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blurredcolor, cv2.COLOR_BGR2HSV)
    
    # Threshold the HSV image to get only black colors
    mask = cv2.inRange(hsv, lower, upper)
    
    # resized = imutils.resize(mask, width=600)
    # cv2.imshow("mask", resized)
    # cv2.waitKey(0)
    
    # Detect lines
    lines = cv2.HoughLines(mask, 1, np.pi/180, 700)
    # If no lines are detected, revert to ratio method
    if (lines is None):
        return measure_crack(image)
    a,b,c = lines.shape
    
    top = []
    bottom = []
    left = []
    right = []
    
    height, width, channels = image.shape
    
    for i in range(a):
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        
        # Sort lines into left, right, top, and bottom
        if (theta < 0.2):
            if (rho < 0.25 * width):
                left.append([rho, theta])
            elif (rho > 0.75 * width):
                right.append([rho, theta])
        elif (theta > 2.94):
            if (rho > -0.25 * width):
                left.append([rho, theta])
            elif (rho < -0.75 * width):
                right.append([rho, theta])
        elif (theta > 1.37 and theta < 1.77):
            if (rho < 0.25 * height):
                top.append([rho, theta])
            elif (rho > 0.75 * height):
                bottom.append([rho, theta])
    
    # If grid line detection fails, revert to ratio method
    if (len(top) == 0 or len(bottom) == 0 or len(left) == 0 or len(right) == 0):
        return measure_crack(image)

    x1, y1 = intersect(top, left)
    x2, y2 = intersect(top, right)
    x3, y3 = intersect(bottom, left)
    x4, y4 = intersect(bottom, right)
    
    # Draw lines on image
    # cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
    # cv2.line(image, (x1, y1), (x3, y3), (0, 255, 0), 5)
    # cv2.line(image, (x2, y2), (x4, y4), (0, 255, 0), 5)
    # cv2.line(image, (x3, y3), (x4, y4), (0, 255, 0), 5)
    
    # Display image with lines drawn
    # resized = imutils.resize(image, width=600)
    # cv2.imshow("lines", resized)
    # cv2.waitKey(0)
    
    # Find perspective transform matrix
    src = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    dst = np.float32([[0, 0], [3000, 0], [0, 3000], [3000, 3000]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    
    # Perspective transform original image
    warped = cv2.warpPerspective(image, matrix, (3000, 3000))
    
    # Display warped image
    # resized = imutils.resize(warped, width=600)
    # cv2.imshow("warped", resized)
    # cv2.waitKey(0)
    
    width, height = blue_rectangle(warped)
    
    # Find larger dimension. Divide by 100 because 100 pixels = 1 cm.
    if (width > height):
        ret = width / 100
    else:
        ret = height / 100
    
    # If dimension is out of bounds, revert to ratio method
    if (ret > 21 or ret < 7):
        return measure_crack(image)
    else:
        return ret

# Find the average intersection point between two sets of lines    
def intersect(lines1, lines2):
    xs = []
    ys = []
    for line1 in lines1:
        a1 = np.cos(line1[1])
        b1 = np.sin(line1[1])
        m1 = -a1 / b1
        x1 = a1 * line1[0]
        y1 = b1 * line1[0]
        b1 = y1 - (x1 * m1)
        for line2 in lines2:
            if (line2[1] == 0.0):
                line2[1] = 0.0001
            a2 = np.cos(line2[1])
            b2 = np.sin(line2[1])
            m2 = -a2 / b2
            x2 = a2 * line2[0]
            y2 = b2 * line2[0]
            b2 = y2 - (x2 * m2)
            x = (b1 - b2) / (m2 - m1)
            y = m1 * x + b1
            xs.append(x)
            ys.append(y)
    meanx = int(sum(xs) / len(xs))
    meany = int(sum(ys) / len(ys))
    return meanx, meany



