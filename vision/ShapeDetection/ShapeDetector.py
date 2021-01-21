import cv2
import imutils
from vision import config
from vision.coral.coral_ui import Coral
from vision.images import get_image
from vision.colors import *
from vision.images import *
import numpy as np

#Debug Mode on
config.debug = True

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        shape = 'unidentified'
        peri = cv2.arcLength(c, True)   # perimeter
        approx = cv2.approxPolyDP(c, 0.04*peri, True)   # use RDP algorithm to simplify shape

        #print(len(approx))
        if len(approx)==2:
            shape = 'line'
        elif len(approx)== 8: #failsafe if color detection fails
            shape = 'star'
        elif len(approx)==4:    # could be square or line
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w/float(h)
            print(ar)
            area = cv2.contourArea(c)
            if area/float(w*h) <= 0.4 or ar <= 0.8 or ar >= 1/0.75:
                shape = 'line'
            else:
                shape = 'square'
        else:
            shape = 'Sponge'    # shapes can only be square, triangle, line, or circle

        return shape


def add_shape(shape, d): 
    if shape in d:
        d[shape] = int(d[shape])+1
    else:
        d[shape] = 1


def detect_shapes(image):
    resized = imutils.resize(image, width=300)  # resize to simplify shapes
    ratio = image.shape[0] / float(resized.shape[0])
    edges = cv2.Canny(image,100,200)
    
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Here we use an adaptive threshold on the image, since we expect the lighting to be non-uniform.
    ret, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    show_debug(otsu, name ="otsu", wait = True)
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
        if c.shape[0] > 2 and area/(resized.shape[0]*resized.shape[1]) > 0.002 and area/(resized.shape[0]*resized.shape[1]) < 0.25:
            cx = int((M["m10"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            cy = int((M["m01"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            shape = sd.detect(c)
            add_shape(shape, num_shapes)

            c = c.astype(float)
            c = c*ratio
            c = c.astype(int)
            cv2.drawContours(image, [c], -1, (255, 0, 0), 2)
            cv2.putText(image, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    show_debug(image)
    return num_shapes

#takes in a 2D array of NumColors arrays of [Blue, Green, Red] values
#sorts the values in order of least to greatest and returns an array containing the order of the RGB values from least to greatest
def get_Order(Color_values, dominant):
    order = [0, 1, 2]
    temp = [0] *3
    for j in range(0, 3):
        temp[j] = Color_values[dominant][j]
    count =0
    while (count < 2):
        for iter in range(0,2):
            if temp[iter] > temp[iter + 1]:
                hold = temp[iter +1]
                temp[iter +1] = temp[iter]
                temp[iter] = hold
                hold = order[iter]
                order[iter] = order[iter + 1]
                order[iter + 1] = hold
        count += 1
    return order

#traverse through 2darray Color_values and find largest value in each color RGB.
def color_check(image):
    resized = imutils.resize(image, width=300)  # resize to simplify shape

    #Number of colors to find in image
    NumColors = 3
    Color_values = get_colors(image, NumColors)

    #Boolean representing lack of nonBlue color
    Blue = True

    #If Red value is largest -> red=star;If blue value is largest ->blue=>send to shapeDetection
    #if (largest - 2nd largest) < (2nd largest - smallest) -> Yellow=fragment
    for dominant in range(0, NumColors):
        order = get_Order(Color_values, dominant)
        if order[2] == 2:
            print("star")
            Blue = False
        elif (Color_values[dominant][order[2]] - Color_values[dominant][order[1]]) < (Color_values[dominant][order[1]] - Color_values[dominant][order[0]]):
            print("fragment")
            Blue = False
    if Blue:
        num_shapes = detect_shapes(image)
        print(num_shapes)


image = get_image("objects", "1", "sponge", "7.jpg")
color_check(image)