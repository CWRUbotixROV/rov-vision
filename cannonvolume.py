import numpy as np
import cv2
import imutils

refPt = [] # array of the coordinates of the points clicked
line = False # we gon draw a line or what? ayy lmao
def clickAndMeasure(event, x, y, flags, param):
# defines the length of the bump-stick
    global refPt
    #line = param[0]

    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x,y)] # a and b are first x and y coordinates for line segment

    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x,y))
        #print(refPt)

def lineLengthMeasurement():
    #print (refPt)
    x1,y1 = refPt[0]
    x2,y2 = refPt[1]
    length = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
    return length

def imageRead():
    global refPt
    image = cv2.imread('real_shapes.png', cv2.IMREAD_COLOR)
    cv2.namedWindow("image")
    clone = image.copy()
    cv2.setMouseCallback("image", clickAndMeasure, [clone])

    while True:
        cv2.imshow('image', image)
        key = cv2.waitKey(1) & 0xFF
        if len(refPt) == 2:
            cv2.line(image,(refPt[0]),(refPt[1]),(0,255,0),thickness=3,lineType=8,shift=0)

        if key == ord("n"):
            refPt = []
            image = clone
        elif key == ord("y"):
            break

    bumpStick = lineLengthMeasurement()
    print(bumpStick)
    clone1 = image.copy()
    cv2.setMouseCallback("image", clickAndMeasure, [clone1])

    while True:
        cv2.imshow('image', image)
        key = cv2.waitKey(1) & 0xFF
        if len(refPt) == 2:
            cv2.line(image,(refPt[0]),(refPt[1]),(0,255,0),thickness=3,lineType=8,shift=0)

        if key == ord("n"):
            refPt = []
            image = clone1
            #cannonVolume = imageRead()
        elif key == ord("y"):
            break
    ratio = lineLengthMeasurement() / bumpStick
    diameter1 = ratio * measure
    radius1 = (0.5) * diameter1
    print("Diameter: " + str(diameter1))
    print("Radius: " + str(radius1))
    
    
measure = float(input("First measurement: "))
cannonVolume = imageRead()