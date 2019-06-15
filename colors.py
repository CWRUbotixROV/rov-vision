import numpy as np
import json
from enum import Enum
import cv2


def setColor(color, lower, upper):
    with open('colors.txt', 'r') as file:
        colors = json.load(file)
    colors[color] = [lower, upper]
    with open('colors.txt', 'w') as outfile:
        json.dump(colors, outfile)

def getMask(color, image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    with open('colors.txt', 'r') as file:
        colors = json.load(file)
    lower, upper = colors[color]
    return cv2.inRange(hsv, np.array(lower), np.array(upper))

def getValues(color):
    with open('colors.txt', 'r') as file:
        colors = json.load(file)
    return colors[color]

def gridLines(image):
    red = getMask('red', image)
    blue = getMask('blue', image)
    mask = cv2.bitwise_not(cv2.bitwise_or(red, blue))
    kernel = np.ones((11, 11), np.uint8)
    eroded = cv2.erode(mask, kernel)

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 7, 6)

    threshAndMask = cv2.bitwise_and(thresh, eroded)

    return threshAndMask