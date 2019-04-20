import cv2
import imutils
import numpy as np

class ShapeDetector:
    def detect(self, c):
        shape = 'unidentified'
        # perimeter
        peri = cv2.arcLength(c, True)   
        # use RDP algorithm to simplify shape
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)   

        # Check what shape is in image
         # shapes can only be square, triangle, line, or circle
        print(len(approx))
        
        areaRatio = 0.4
        arUpper = 0.8
        arLower = (1/0.75)
        if len(approx)==2:
            shape = 'line'
        elif len(approx)==3:
            shape = 'triangle'
        # Check if square or line
        elif len(approx)==4:    
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w/float(h)
            print(ar)
            area = cv2.contourArea(c)
            if area/float(w*h) <= areaRatio or ar <= arUpper or ar >= arLower:
                shape = 'line'
            else:
                shape = 'square'
        else:
            shape = 'circle'   

        return shape


def add_shape(shape, d):
    if shape in d:
        d[shape] = int(d[shape])+1
    else:
        d[shape] = 1


def detect_shapes():
    image = cv2.imread('real_shapes.png', cv2.IMREAD_COLOR)
    blank = cv2.imread('blank.png', cv2.IMREAD_COLOR)
    resized = imutils.resize(image, width=300)  # resize to simplify shapes
    ratio = image.shape[0] / float(resized.shape[0])
    edges = cv2.Canny(image,100,200)
    
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use an adaptive threshold on the image, since lighting is expected to be non-uniform.
    ret, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imshow("otsu", otsu)
    cv2.waitKey(0)

    num_shapes = {}

    cnts_ = cv2.findContours(otsu.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = None
    if cv2.__version__[0]=='3':
        cnts = cnts_[1]
    else:
        cnts = cnts_[0]
    sd = ShapeDetector()

    for c in cnts:
        area = cv2.contourArea(c)
        # compute centroid of the contour as it would be on the original image
        M = cv2.moments(c)

        # ignore contours that are too small to be species
        upperContourThresh = 0.25
        lowerContourThresh = 0.002
        if c.shape[0] > 2 and area/(resized.shape[0]*resized.shape[1]) > lowerContourThresh and area/(resized.shape[0]*resized.shape[1]) < upperContourThresh:
            cx = int((M["m10"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            cy = int((M["m01"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            shape = sd.detect(c)
            add_shape(shape, num_shapes)

            c = c.astype(float)
            c = c*ratio
            c = c.astype(int)
            cv2.drawContours(image, [c], -1, (255, 0, 0), 2)
            cv2.putText(image, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
	
    # Draw line, Square, Circle and Triangle shapes
    lineCoord1 = (25,25)
    lineCoord2 = (190,45)
    line = cv2.rectangle(blank,lineCoord1,lineCoord2, (0,0,255),-1)

    squareCoord1 = (50,95)
    squareCoord2 = (150,200)
    square = cv2.rectangle(blank,squareCoord1, squareCoord2, (0,0,255),-1)

    circleCoord1 = (100,275)
    circleRadius = 50
    circle = cv2.circle(blank, circleCoord1, circleRadius, (0,0,255),-1)

    triangleCoord1 = (100,350)
    triangleCoord2 = (50,450)
    triangleCoord3 = (150,450)
    triangle = np.array([triangleCoord1,triangleCoord2,triangleCoord3])
    triangle = cv2.drawContours(blank, [triangle], 0, (0,0,255), -1)

    # Display number of shapes next to each shape
    font = cv2.FONT_HERSHEY_SIMPLEX

    lineNCoord = (400,75)
    LineNumb = cv2.putText(blank,str(num_shapes['line']),lineNCoord,font,3,(0,0,255),2,cv2.LINE_AA)

    squareNCoord = (400,175)
    SquareNumb = cv2.putText(blank,str(num_shapes['square']),squareNCoord,font,3,(0,0,255),2,cv2.LINE_AA)
    
    circleNCoord = (400,290)
    CircleNumb = cv2.putText(blank,str(num_shapes['circle']), circleNCoord,font,3,(0,0,255),2,cv2.LINE_AA)
    
    triangleNCoord =(400,430)
    TriangleNumb = cv2.putText(blank,str(num_shapes['triangle']),triangleNCoord,font,3,(0,0,255),2,cv2.LINE_AA)
    
    cv2.imshow("Image", image)

    # Display Results
    cv2.imshow("Line", line)
    cv2.waitKey(0)
    return num_shapes

num_shapes = detect_shapes()
print(num_shapes)
