import cv2
import numpy as np
import imutils

SIZE = 1200

def nothing(x):
    pass

THRESH = 15
def loadPixel(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        x = int((float(width) / SIZE) * x)
        y = int((float(width) / SIZE) * y)
        h, s, v = hsv[y][x]

        cv2.setTrackbarPos('H1', 'image', h)
        cv2.setTrackbarPos('S1', 'image', s)
        cv2.setTrackbarPos('V1', 'image', v)
        cv2.setTrackbarPos('H2', 'image', THRESH)
        cv2.setTrackbarPos('S2', 'image', THRESH)
        cv2.setTrackbarPos('V2', 'image', THRESH)


# Read calibration image
image = cv2.imread("calibrate.png")
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
height, width, channels = image.shape

cv2.namedWindow('image')
cv2.namedWindow('original')
resized = imutils.resize(image, width=SIZE)
cv2.imshow('original', resized)
cv2.setMouseCallback('original', loadPixel)
cv2.createButton('test', loadPixel)

# create trackbars for color change
cv2.createTrackbar('H1','image',0,180,nothing)
cv2.createTrackbar('H2','image',0,180,nothing)
cv2.createTrackbar('S1','image',0,255,nothing)
cv2.createTrackbar('S2','image',0,255,nothing)
cv2.createTrackbar('V1','image',0,255,nothing)
cv2.createTrackbar('V2','image',0,255,nothing)

cv2.setTrackbarPos('H2', 'image', 180)
cv2.setTrackbarPos('S2', 'image', 255)
cv2.setTrackbarPos('V2', 'image', 255)



while(1):
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

    # get current positions of four trackbars
    h1 = cv2.getTrackbarPos('H1','image')
    h2 = cv2.getTrackbarPos('H2','image')
    s1 = cv2.getTrackbarPos('S1','image')
    s2 = cv2.getTrackbarPos('S2','image')
    v1 = cv2.getTrackbarPos('V1','image')
    v2 = cv2.getTrackbarPos('V2','image')

    lower = np.array([h1 - h2, s1 - s2, v1 - v2])
    upper = np.array([h1 + h2, s1 + s2, v1 + v2])

    mask = cv2.inRange(hsv, lower, upper)
    resized = imutils.resize(mask, width=SIZE)
    cv2.imshow('image', resized)



    

cv2.destroyAllWindows()