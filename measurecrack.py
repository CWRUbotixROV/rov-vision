import cv2, imutils
import numpy as np

def measure_crack(image):
    #image = cv2.imread('crack3.jpg', cv2.IMREAD_COLOR)
    
    width, height = blue_rectangle(image)
    
    if height > width:
        return (height/width)*1.85
    else:
        return (width/height)*1.85
    	
def blue_rectangle(image):
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
    return width, height

def measure_crack2(image):
    #image = cv2.imread('crack5.jpg', cv2.IMREAD_COLOR)
    
    # define range of color in HSV
    lower = np.array([0,0,0])
    upper = np.array([180,50,100])

    
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    blurredcolor = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blurredcolor, cv2.COLOR_BGR2HSV)
    
    # Threshold the HSV image to get only black colors
    mask = cv2.inRange(hsv, lower, upper)
    
    resized = imutils.resize(mask, width=600)
    cv2.imshow("mask", resized)
    cv2.waitKey(0)
    
    # Canny line detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    resized = imutils.resize(edges, width=600)
    #cv2.imshow("edges", resized)
    #cv2.waitKey(0)
    
    lines = cv2.HoughLines(mask, 1, np.pi/180, 700)
    a,b,c = lines.shape
    
    top = []
    bottom = []
    left = []
    right = []
    
    height, width, channels = image.shape
    
    for i in range(a):
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        
        #Sort lines
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
        
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 10000*(-b))
        y1 = int(y0 + 10000*(a))
        x2 = int(x0 - 10000*(-b))
        y2 = int(y0 - 10000*(a))
        #print(str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2))
        #cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
    
    #print(left)
    #print(right)
    #print(top)
    #print(bottom)
    
    x1, y1 = intersect(top, left)
    x2, y2 = intersect(top, right)
    x3, y3 = intersect(bottom, left)
    x4, y4 = intersect(bottom, right)
    
    cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
    cv2.line(image, (x1, y1), (x3, y3), (0, 255, 0), 5)
    cv2.line(image, (x2, y2), (x4, y4), (0, 255, 0), 5)
    cv2.line(image, (x3, y3), (x4, y4), (0, 255, 0), 5)
    
    
    resized = imutils.resize(image, width=600)
    cv2.imshow("lines", resized)
    cv2.waitKey(0)
    
    src = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    dst = np.float32([[0, 0], [3000, 0], [0, 3000], [3000, 3000]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    
    warped = cv2.warpPerspective(image, matrix, (3000, 3000))
    
    resized = imutils.resize(warped, width=600)
    cv2.imshow("warped", resized)
    cv2.waitKey(0)
    
    width, height = blue_rectangle(warped)
    
    if (width > height):
        return width / 100
    else:
        return height / 100
    
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
            
image = cv2.imread('crack4.jpg', cv2.IMREAD_COLOR)
print(measure_crack(image))
print(measure_crack2(image))



