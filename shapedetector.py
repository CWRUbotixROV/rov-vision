import cv2
import argparse
import imutils
import numpy as np
import sys
ROI_SIDE = 800

# detects number and type of shapes on an image
class ShapeDetector:
    def __init__(self):
        pass
    
    def detect(self, c):
    # defines shape parameters to differentiate shapes
        shape = 'unidentified'
        peri = cv2.arcLength(c, True)   # perimeter
        approx = cv2.approxPolyDP(c, 0.04*peri, True)   # use RDP algorithm to simplify shape

        print(len(approx))
        if len(approx)==2:
            shape = 'line'
        elif len(approx)==3:
            shape = 'triangle'
        elif len(approx)==4:    # could be square or line
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w/float(h)
            print(ar)
            area = cv2.contourArea(c)
            if area/float(w*h) <= 0.4 or ar <= 0.8 or ar >= 1/0.8:
                shape = 'line'
            else:
                shape = 'square'
        else:
            shape = 'circle'    # shapes can only be square, triangle, line, or circle

        return shape

    def add_shape(self, shape, d):
    # counts numbers of shapes
        if shape in d:
            d[shape] = int(d[shape])+1
        else:
            d[shape] = 1

refPt = [] # refPt identifies the cropped part of the image
cropping = False 
def click_and_crop(event, x, y, flags, param):
    # creates a new cropped image
        global refPt, cropping
        image = param[0]

        if event == cv2.EVENT_LBUTTONDOWN:
            refPt = [(x , y)] # a and b are x and y coordinates for cropped section
            cropping = True

        elif event == cv2.EVENT_LBUTTONUP:
            refPt.append((x , y))
            cropping = False

        cv2.imshow("image", image)        

def detect_shapes():
    image = cv2.imread(sys.argv[1], cv2.IMREAD_COLOR)
    blank = cv2.imread('blank.png', cv2.IMREAD_COLOR) 
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop, [clone])

    # while True:
    #     cv2.imshow("image",image)
    #     key = cv2.waitKey(1) & 0xFF

    #     if key == ord("r"): # press r to reset and take a new crop
    #         image = clone.copy()

    #     elif key == ord("c"): # press c to crop image
    #         break
    if len(refPt) == 2:
        roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
        cv2.imshow("ROI",roi)
        cv2.waitKey(0)

    imw = image.shape[0]
    imh = image.shape[1]
    roi =  image[(imw-ROI_SIDE)//2:(imw+ROI_SIDE)//2, (imh-ROI_SIDE)//2:(imh+ROI_SIDE)//2]
    resized = imutils.resize(roi, width=300)  # resize to simplify shapes
    ratio = roi.shape[0] / float(resized.shape[0])

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Here we use an adaptive threshold on the image, since we expect the lighting to be non-uniform.
    ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    cv2.imshow("thresh", thresh)
    # cv2.waitKey(0)

    num_shapes = {'square':0,'line':0,'circle':0,'triangle':0}

    cnts_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
        if c.shape[0] > 2 and area/(resized.shape[0]*resized.shape[1]) > 0.002:
            cx = int((M["m10"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            cy = int((M["m01"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            shape = sd.detect(c)
            sd.add_shape(shape, num_shapes)

            c = c.astype(float)
            c = c*ratio
            c = c.astype(int)
            cv2.drawContours(roi, [c], -1, (255, 0, 0), 2)
            cv2.putText(roi, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # cv2.imshow("ROI", roi)
            # cv2.waitKey(0)
    #Draw line, square, circle, and triangle shapes
    #Coordinates determined through trial and error until appropriate proportions of shapes were found

    LINE_COORD1 = (25,25)
    LINE_COORD2 = (190,45)
    line = cv2.rectangle(blank, LINE_COORD1, LINE_COORD2, (0,0,255), -1)

    SQUARE_COORD1 = (50,95)
    SQUARE_COORD2 = (150,200)
    square = cv2.rectangle(blank, SQUARE_COORD1, SQUARE_COORD2, (0,0,255), -1)

    CIRCLE_CENTER = (100, 275)
    CIRCLE_RADIUS = 50
    circle = cv2.circle(blank, CIRCLE_CENTER, CIRCLE_RADIUS, (0,0,255), -1)

    TRIANGLE_COORD1 = (100,350)
    TRIANGLE_COORD2 = (50,450)
    TRIANGLE_COORD3 = (150,450)
    triangle = np.array([TRIANGLE_COORD1, TRIANGLE_COORD2, TRIANGLE_COORD3])
    triangle = cv2.drawContours(blank, [triangle], 0, (0,0,255), -1)

    #Display number of shapes next to each shape
    #Coordinates determined through trial and error until each number was across from its corresponding shape
    font = cv2.FONT_HERSHEY_SIMPLEX

    LINE_NUMB_COORD = (400,75)
    LineNumb = cv2.putText(blank, str(num_shapes['line']), LINE_NUMB_COORD, font, 3, (0,0,255), 2, cv2.LINE_AA)

    SQUARE_NUMB_COORD = (400,175)
    SquareNumb = cv2.putText(blank, str(num_shapes['square']), SQUARE_NUMB_COORD, font, 3, (0,0,255), 2, cv2.LINE_AA)
    
    CIRCLE_NUMB_COORD = (400,290)
    CircleNumb = cv2.putText(blank, str(num_shapes['circle']), CIRCLE_NUMB_COORD, font, 3, (0,0,255), 2, cv2.LINE_AA)

    TRIANGLE_NUMB_COORD = (400,430)
    TriangleNumb = cv2.putText(blank, str(num_shapes['triangle']), TRIANGLE_NUMB_COORD, font, 3, (0,0,255), 2, cv2.LINE_AA)

    #cv2.imshow("Image",image)

    #Display results
    if __name__ == "__main__":
        cv2.imshow("ROI", roi)
        cv2.imshow("Line", line)
        cv2.waitKey(0)
        return num_shapes

    #cv2.imshow("ROI", roi)
    #cv2.imwrite('image.png', image)
    #cv2.waitKey(0)
    #return num_shapes

if __name__=='__main__':
    # stream from Video object
    num_shapes = detect_shapes()
    print(num_shapes)
