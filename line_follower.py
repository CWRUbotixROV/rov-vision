import cv2
import numpy as np

import gi, time
from video import Video
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    HOLD = 0

def centerline(box):
    """
    Takes a bounding rectangle and return two things: the centerline as a line segment, and whether it is vertical.
    """
    x, y, w, h = box
    if w >= h:
        return np.array([[x, y+h/2], [x+w, y+h/2]]), False
    else:
        return np.array([[x+w/2, y], [x+w/2, y+h]]), True


class LineFollower:
    stream = None
    img = None
    cnt_crack = None
    found = False
    last_time = 0
    found = False
    moving = Direction.STOP

    def __init__(self, port):
        self.stream = Video(port=port)

    def set_moving(self, m):
        self.moving = m
    
    def next_direction(self):
        nextdir = Direction.STOP

        if not self.stream.frame_available():
            return nextdir
        img = self.stream.frame()
        height, width, _ = img.shape

        new_time = time.time()
        print(1/float(new_time-self.last_time))  # update rate, for debugging
        self.last_time = new_time

        # img = cv2.imread('/home/sam/Pictures/screwdriver.jpg')
        # img = cv2.GaussianBlur(img, (5, 5), 0)
        lower_red = np.array([0, 0, 50])
        upper_red = np.array([80, 80, 255])
        lower_blue = np.array([50, 0, 0])
        upper_blue = np.array([255, 50, 50])

        # apply masks
        mask_red = cv2.inRange(img, lower_red, upper_red)
        mask_blue = cv2.inRange(img, lower_blue, upper_blue)
        im_red = cv2.bitwise_and(img, img, mask=mask_red)
        im_blue = cv2.bitwise_and(img, img, mask=mask_blue)

        # threshold
        im_red = cv2.threshold(im_red, 60, 255, cv2.THRESH_BINARY)[1]
        im_blue = cv2.threshold(im_blue, 60, 255, cv2.THRESH_BINARY)[1]

        # flatten so findContours doesn't get mad
        im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)
        im_blue = cv2.cvtColor(im_blue, cv2.COLOR_BGR2GRAY)

        # find contours
        cr = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cb = cv2.findContours(im_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if cv2.__version__[0]=='3':
            contours_r = cr[1]
            contours_b = cb[1]
        else:
            contours_r = cr[0]
            contours_b = cb[0]

        if len(contours_r) > 0:
            biggest = max(contours_r, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(biggest)
            if cv2.contourArea(biggest)/(x*y) > 2.5:    # this is a corner
                # What we are doing is figuring out which quadrant the bounding box is in.
                # This works because we know, from the rules on FOV, that corners will always be touching 
                # two sides of the frame, so the distance between the bounding box and the side is 0. 
                is_right = width-2*x-w < 0 
                is_up = height-2*y-h >= 0
                if is_right and is_up:
                    if self.moving==Direction.DOWN: # can only be moving down or left to get this
                        nextdir = Direction.RIGHT  if w/h>1 else Direction.DOWN
                    elif self.moving==Direction.LEFT:
                        nextdir = Direction.LEFT  if w/h>1 else Direction.UP
                    else:
                        nextdir = self.moving
                elif is_right and not is_up:
                    if self.moving==Direction.UP:
                        nextdir = Direction.RIGHT  if w/h>1 else Direction.UP
                    elif self.moving==Direction.LEFT:
                        nextdir = Direction.LEFT  if w/h>1 else Direction.DOWN
                    else:
                        nextdir = self.moving
                elif not is_right and is_up:
                    if self.moving==Direction.DOWN:
                        nextdir = Direction.LEFT  if w/h>1 else Direction.DOWN
                    elif self.moving==Direction.RIGHT:
                        nextdir = Direction.RIGHT  if w/h>1 else Direction.UP
                    else:
                        nextdir = self.moving
                else:
                    if self.moving==Direction.UP:
                        nextdir = Direction.LEFT  if w/h>1 else Direction.UP
                    elif self.moving==Direction.RIGHT:
                        nextdir = Direction.RIGHT  if w/h>1 else Direction.DOWN
                    else:
                        nextdir = self.moving

            if len(contours_b) > 0:
                crack = max(contours_b, key=cv2.contourArea)
                if cv2.contourArea(crack) > 1000:
                    print('Crack found!')
                    x, y, w, h = cv2.boundingRect(crack)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    self.cnt_crack = crack
                    self.found = True
        else:
            nextdir = Direction.STOP
        
        return nextdir
        
        # # Note: Showing the image makes the loop run a LOT slower
        # cv2.imshow('image', img)
        # if (cv2.waitKey(1) & 0xFF == ord('q')) or self.found:
        #     return 'end'
