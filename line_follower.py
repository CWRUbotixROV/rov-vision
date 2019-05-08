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

MIN_TURNS = 3

class Direction(Enum):
    """
    Enum for directions
    """
    UP = 1
    DOWN = -1
    LEFT = -2
    RIGHT = 2
    STOP = 0
    def __neg__(self):
        return Direction(-self.value)
    def __repr__(self):
        if self.value==1:
            return "UP"
        elif self.value==-1:
            return "DOWN"
        elif self.value==-2:
            return "LEFT"
        elif self.value==2:
            return "RIGHT"
        else:
            return "STOP"


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
    stream = None               # The video stream object
    img = None                  # The current image     
    moving = Direction.STOP     # The direction the robot is actually moving in
    lost_line = False           # Whether we lost track of the red line
    last_dir = Direction.STOP   # The last direction in which we were following the line
    last_centroid = (0, 0)      # The last centroid of the red line
    turn_count = {Direction.UP:0, Direction.DOWN:0, Direction.LEFT:0, Direction.RIGHT:0}
    in_turn = False

    def __init__(self, port=None):
        if port is not None:
            self.stream = Video(port=port)

    def set_moving(self, m):
        """
        Set the value of `moving`, the attibute for the direction of motion.
        """
        if m in Direction:
            self.moving = m
    
    def drawInfo(self, drawn, x, y, w, h, biggest, nextdir):
        drawn = cv2.rectangle(drawn, (x, y), (x+w, y+h), (0, 0, 255), 5)
        drawn = cv2.drawContours(drawn, [biggest], -1, (0,255,0), 4)
        drawn = cv2.line(drawn, self.last_centroid, self.last_centroid, (255,0,255), 10)
        cv2.putText(drawn, str(nextdir), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
        cv2.putText(drawn, str(self.last_dir), (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
        cv2.putText(drawn, str(self.in_turn), (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0,0), 2)
        return drawn
    
    def centroid_side(self, height, width):
        """
        Determines the side of the frame on which the red line appeared to exit the frame.
        
        Arguments:
            height : the height of the frame in pixels
            width : the width of the frame in pixels
        
        Returns:
            Direction : the direction for the side (up, down, left, right)
        """
        x = self.last_centroid[0]-(width/2)
        y = (height/2)-self.last_centroid[1]

        # We divide the frame into 4 regions with the lines y=x and y=-x, and determine the side based on which
        # region the centroid was in last.
        if y > x and y > -x:
            return Direction.UP
        elif y > x and y <= -x:
            return Direction.LEFT
        elif y <= x and y <= -x:
            return Direction.DOWN
        else:
            return Direction.RIGHT
    
    def mask_for_red(self, img):
        lower_red = np.array([0, 0, 80])    # [0, 0, 20] in water
        upper_red = np.array([80, 80, 255]) # [3, 3, 255] in water

        im_red = cv2.GaussianBlur(img, (5,5), 0)   # smooth image

        # apply mask for red
        mask_red = cv2.inRange(im_red, lower_red, upper_red)
        im_red = cv2.bitwise_and(im_red, im_red, mask=mask_red)

        # threshold
        im_red = cv2.threshold(im_red, 30, 255, cv2.THRESH_BINARY)[1]

        # flatten so findContours doesn't get mad
        im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)
        return im_red

    def handle_image(self, img, show=False):
        """
        Processes an image and returns the next direction for the ROV to move.

        Arguments:
            img: the OpenCV image to process
            show (bool): whether to display the processed image
        """
        nextdir = self.last_dir
        height, width, _ = img.shape

        im_red = self.mask_for_red(img)

        # find contours
        cr = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_r = cr[0]

        drawn = img
        nextdir = self.moving

        if len(contours_r) > 0:
            biggest = max(contours_r, key=cv2.contourArea)

            if cv2.contourArea(biggest) < 100:
                return nextdir, drawn
            
            M = cv2.moments(biggest)
            self.last_centroid = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
            x, y, w, h = cv2.boundingRect(biggest)
            hull = cv2.convexHull(biggest) 
            boundingRect = cv2.minAreaRect(hull)
            boundingRect = cv2.boxPoints(boundingRect)
            boundingRect = np.int0(boundingRect)
            hull_area = cv2.contourArea(hull)

            is_right = x > width - (x + w)
            is_up = y <= height - (y + h)

            if self.lost_line:      # lost the line and found it again
                nextdir = self.last_dir
                self.lost_line = False
                drawn = self.drawInfo(drawn, x, y, w, h, biggest, nextdir)
                return nextdir, drawn

            if (w*h)/cv2.contourArea(biggest) > 3:    # this is a corner
                # What we are doing is figuring out which quadrant the bounding box is in.
                # This works because we know, from the rules on FOV, that corners will always be touching 
                # two sides of the frame, so the distance between the bounding box and the side is 0.
                self.in_turn = True
                if is_right and is_up:
                    if self.last_dir==Direction.DOWN: # can only be moving down or left to get this
                        nextdir = Direction.RIGHT
                    elif self.last_dir==Direction.LEFT:
                        nextdir = Direction.UP
                    else:
                        nextdir = self.last_dir
                elif is_right and not is_up:
                    if self.last_dir==Direction.UP:
                        nextdir = Direction.RIGHT
                    elif self.last_dir==Direction.LEFT:
                        nextdir = Direction.DOWN
                    else:
                        nextdir = self.last_dir
                elif not is_right and is_up:
                    if self.last_dir==Direction.DOWN:
                        nextdir = Direction.LEFT
                    elif self.last_dir==Direction.RIGHT:
                        nextdir = Direction.UP
                    else:
                        nextdir = self.last_dir
                else:
                    if self.last_dir==Direction.UP:
                        nextdir = Direction.LEFT
                    elif self.last_dir==Direction.RIGHT:
                        nextdir = Direction.DOWN
                    else:
                        nextdir = self.last_dir

            else:
                print("Straight segment")
                nextdir = self.last_dir
                self.in_turn = False

            drawn = self.drawInfo(drawn, x, y, w, h, biggest, nextdir)

            if show:
                print("is_right: {0}".format(is_right))
                print("is_up: {0}".format(is_up))
                cv2.imshow('image', drawn)
                cv2.waitKey(0)

            self.last_dir = nextdir

        else:
            self.lost_line = True
            nextdir = self.centroid_side(height, width) # Move toward the side where we lost the line
            cv2.putText(drawn, str(nextdir), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
            cv2.putText(drawn, str(self.last_dir), (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
            cv2.putText(drawn, str(self.in_turn), (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0,0), 2)
        
        return nextdir, drawn

    
    def next_direction(self, show=False):
        """
        Gives the next direction (from the Direction enum), determined from the video stream.
        """
        nextdir = self.moving

        if self.stream is None:
            print("No port specified!")
            return Direction.STOP

        if not self.stream.frame_available():
            return nextdir, None
        img = self.stream.frame()
        return self.handle_image(img, show=show)

if __name__ == '__main__':
    cap = cv2.VideoCapture('/home/sam/Pictures/2019/05/07/IMG_1560.MOV')
    lf = LineFollower()
    lf.last_dir = Direction.RIGHT
    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break
        direction, img = lf.handle_image(frame)
        lf.set_moving(direction)
        print(f"Next direction: {direction}")
        cv2.imshow('Video', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

