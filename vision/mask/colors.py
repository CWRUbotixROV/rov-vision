import numpy as np
import json
from enum import Enum
import cv2
import pkgutil

def get_data():
    data = pkgutil.get_data(__name__, "colors.txt")
    json_data = json.loads(data.decode())
    return json_data


def set_color(color, lower, upper):
    with open('colors.txt', 'r') as file:
        colors = json.load(file)
    colors[color] = [lower, upper]
    with open('colors.txt', 'w') as outfile:
        json.dump(colors, outfile)

def get_mask(color, image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    colors = get_data()
    lower, upper = colors[color]
    return cv2.inRange(hsv, np.array(lower), np.array(upper))

def get_values(color):
    colors = get_data()
    return colors[color]

def grid_lines(image):
    red = get_mask('red', image)
    blue = get_mask('blue', image)
    mask = cv2.bitwise_not(cv2.bitwise_or(red, blue))
    kernel = np.ones((15, 15), np.uint8)
    eroded = cv2.erode(mask, kernel)

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 7, 6)

    threshAndMask = cv2.bitwise_and(thresh, eroded)

    return threshAndMask