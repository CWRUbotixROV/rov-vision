import cv2
import numpy as np
import imutils
import colors

SIZE = 650

def nothing(x):
    pass

THRESH = 20
def loadPixel(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        x = int((float(width) / SIZE) * x)
        y = int((float(width) / SIZE) * y)
        h, s, v = hsv[y][x]

        cv2.setTrackbarPos('H1', 'image', h - THRESH)
        cv2.setTrackbarPos('S1', 'image', s - THRESH)
        cv2.setTrackbarPos('V1', 'image', v - THRESH)
        cv2.setTrackbarPos('H2', 'image', h + THRESH)
        cv2.setTrackbarPos('S2', 'image', s + THRESH)
        cv2.setTrackbarPos('V2', 'image', v + THRESH)


# Read calibration image
image = cv2.imread("calibrate.png")
video = cv2.VideoCapture("/home/vm/Downloads/line.mp4")
#retval, image = video.read()
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
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
    elif k == 115:
        color = input("Set color: ")
        colors.setColor(color, [h1, s1, v1], [h2, s2, v2])
    elif k == 108:
        color = input("Load color: ")
        lower, upper = colors.getValues(color)
        h1, s1, v1 = lower
        h2, s2, v2 = upper
        cv2.setTrackbarPos('H1', 'image', h1)
        cv2.setTrackbarPos('S1', 'image', s1)
        cv2.setTrackbarPos('V1', 'image', v1)
        cv2.setTrackbarPos('H2', 'image', h2)
        cv2.setTrackbarPos('S2', 'image', s2)
        cv2.setTrackbarPos('V2', 'image', v2)

    # get current positions of four trackbars
    h1 = cv2.getTrackbarPos('H1','image')
    h2 = cv2.getTrackbarPos('H2','image')
    s1 = cv2.getTrackbarPos('S1','image')
    s2 = cv2.getTrackbarPos('S2','image')
    v1 = cv2.getTrackbarPos('V1','image')
    v2 = cv2.getTrackbarPos('V2','image')

    lower = np.array([h1, s1, v1])
    upper = np.array([h2, s2, v2])

    mask = cv2.inRange(hsv, lower, upper)
    resized = imutils.resize(mask, width=SIZE)
    cv2.imshow('image', resized)



    

cv2.destroyAllWindows()