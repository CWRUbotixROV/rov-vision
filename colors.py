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