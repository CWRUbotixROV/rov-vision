"""
Code for line following
"""
from enum import Enum
import cv2
import numpy as np
from video import Video

"""
NOTE 5/3/2019: All of the blue is missing from the underwater footage. This might be a problem.
"""

class Direction(Enum):
    """
    Enum for directions
    """
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    STOP = "STOP"

def centerline(box):
    """
    Takes a bounding rectangle and return two things: the centerline as a line segment, 
    and whether it is vertical.
    """
    x, y, w, h = box
    if w >= h:
        return np.array([[x, y+h/2], [x+w, y+h/2]]), False
    return np.array([[x+w/2, y], [x+w/2, y+h]]), True


class LineFollower:
    """
    Given a port for a video stream, allows the user to call the next_direction method to get the next direction
    for line following.
    """
    stream = None
    img = None
    cnt_crack = None
    found = False
    last_time = 0
    found = False
    moving = Direction.STOP

    def __init__(self, port=None):
        if port is not None:
            self.stream = Video(port=port)

    def set_moving(self, m):
        """
        Set the value of `moving`, the attibute for the direction of motion.
        """
        if m in Direction:
            self.moving = m

    def handle_image(self, img, show=False):
        """
        Processes an image and returns the next direction for the ROV to move.

        Arguments:
            img: the OpenCV image to process
            show (bool): whether to display the processed image
        """
        nextdir = Direction.STOP
        height, width, _ = img.shape

        lower_red = np.array([0, 0, 30])
        upper_red = np.array([3, 3, 255])

        img = cv2.GaussianBlur(img, (5,5), 0)   # smooth image

        # apply mask for red
        mask_red = cv2.inRange(img, lower_red, upper_red)
        im_red = cv2.bitwise_and(img, img, mask=mask_red)

        # threshold
        im_red = cv2.threshold(im_red, 30, 255, cv2.THRESH_BINARY)[1]

        # flatten so findContours doesn't get mad
        im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)

        # find contours
        cr = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_r = cr[0]

        drawn = img

        if len(contours_r) > 0:
            biggest = max(contours_r, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(biggest)
            is_right = width-2*x-w < 0 
            is_up = height-2*y-h >= 0

            # Turn conditions: Currently, they are designed to be true when we've crossed the centerline of the
            # line perpendicular to our current direction of motion. The idea is to turn then, so we stay centered
            # on the line.
            turn_x = width/w>2
            turn_y = height/h>2

            if(show):
                drawn = cv2.drawContours(drawn, [biggest], -1, (0, 255, 0), 3)

            if (w*h)/cv2.contourArea(biggest) > 2:    # this is a corner
                # What we are doing is figuring out which quadrant the bounding box is in.
                # This works because we know, from the rules on FOV, that corners will always be touching 
                # two sides of the frame, so the distance between the bounding box and the side is 0.
                if is_right and is_up:
                    if self.moving==Direction.DOWN: # can only be moving down or left to get this
                        nextdir = Direction.RIGHT  if turn_y else Direction.DOWN
                    elif self.moving==Direction.LEFT:
                        nextdir = Direction.UP  if turn_x else Direction.LEFT
                    else:
                        nextdir = self.moving
                elif is_right and not is_up:
                    if self.moving==Direction.UP:
                        nextdir = Direction.RIGHT  if turn_y else Direction.UP
                    elif self.moving==Direction.LEFT:
                        nextdir = Direction.DOWN  if turn_x else Direction.LEFT
                    else:
                        nextdir = self.moving
                elif not is_right and is_up:
                    if self.moving==Direction.DOWN:
                        nextdir = Direction.LEFT  if turn_y else Direction.DOWN
                    elif self.moving==Direction.RIGHT:
                        nextdir = Direction.UP if turn_x else Direction.RIGHT
                    else:
                        nextdir = self.moving
                else:
                    if self.moving==Direction.UP:
                        nextdir = Direction.LEFT  if turn_y else Direction.UP
                    elif self.moving==Direction.RIGHT:
                        nextdir = Direction.DOWN  if turn_x else Direction.RIGHT
                    else:
                        nextdir = self.moving
            # elif h >= 0.95*height:
            #     nextdir = Direction.UP if self.moving==Direction.UP else Direction.DOWN
            # elif w>=0.95*width:
            #     nextdir = Direction.RIGHT if self.moving==Direction.RIGHT else Direction.LEFT
            
            else:
                nextdir = self.moving

            if show:
                print("is_right: {0}".format(is_right))
                print("is_up: {0}".format(is_up))
                drawn = cv2.rectangle(drawn, (x, y), (x+w, y+h), (0, 0, 255), 5)
                cv2.imshow('image', drawn)
                cv2.waitKey(0)

        else:
            nextdir = self.moving
        
        return nextdir
        
        # # Note: Showing the image makes the loop run a LOT slower
        # cv2.imshow('image', img)
        if (cv2.waitKey(1) & 0xFF == ord('q')) or self.found:
            return 'end'
    
    def next_direction(self):
        """
        Gives the next direction (from the Direction enum), determined from the video stream.
        """
        nextdir = Direction.STOP

        if self.stream is None:
            print("No port specified!")
            return Direction.STOP

        if not self.stream.frame_available():
            return nextdir
        img = self.stream.frame()
        return self.handle_image(img)

if __name__ == '__main__':
    image = cv2.imread('line_underwater.png')
    lf = LineFollower()
    lf.set_moving(Direction.DOWN)
    print(f"Next direction: {lf.handle_image(image, show=True)}")

