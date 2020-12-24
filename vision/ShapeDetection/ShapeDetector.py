import cv2
import imutils
from vision.coral.coral_ui import Coral
from vision.images import get_image
import numpy as np

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
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
            if area/float(w*h) <= 0.4 or ar <= 0.8 or ar >= 1/0.75:
                shape = 'line'
            else:
                shape = 'square'
        else:
            shape = 'circle'    # shapes can only be square, triangle, line, or circle

        return shape


def add_shape(shape, d):
    if shape in d:
        d[shape] = int(d[shape])+1
    else:
        d[shape] = 1


def detect_shapes():
    image = get_image("coral", "1", "1.jpg")
    resized = imutils.resize(image, width=300)  # resize to simplify shapes
    ratio = image.shape[0] / float(resized.shape[0])
    edges = cv2.Canny(image,100,200)
    
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Here we use an adaptive threshold on the image, since we expect the lighting to be non-uniform.
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


    cv2.imshow("Image", image)
    cv2.imwrite('image.png', image)
    cv2.waitKey(0)
    return num_shapes


num_shapes = detect_shapes()
print(num_shapes)