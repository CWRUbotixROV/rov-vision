import cv2
import numpy as npz
from line_follower import LineFollower, Direction
import imutils

lf = LineFollower()
lf.set_moving(Direction.DOWN)
img = cv2.imread("/home/sam/Downloads/IMG_1311_1.JPG")
img = imutils.resize(img, height=1000)
next_dir = lf.handle_image(img, show=True)
print(next_dir)
