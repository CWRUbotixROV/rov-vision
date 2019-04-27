import cv2
import numpy as np
from enum import Enum
import sys

class Direction(Enum):
    neutral = 0
    left = 1
    up = 2
    right = 3
    down = 4

class LineFollower:
    """determines direction ROV should be moving based on input of picture with line"""

    direction = Direction.neutral      # direction the ROV should move in to follow line
    immediate_dir = Direction.neutral  # currently registered direction
    next_dir = Direction.neutral       # will be direction when turn decreases    
    change_dir_count = 5               # number of registerd turns needed until direction changes
    turn = 1000000                     # threshold for average of dir_change to determine a turn
    find_turn = False                  # true when program is currently determining a turn direction
    dir_change = []                    # queue of bounding rect area/hull area from previous five images    
    is_moving = True                   # determines when line_following stops

    START_ANGLE_BARRIER = 45           # barrier angle for whether line start it to the right or down
    END_OF_LINE_SOLIDITY = 0.7         # solidity determine end of line
    MIN_GROUP_MULTIPLIER = 0.8         # min to group values when determing direction
    MAX_GROUP_MULTIPLIER = 1.2         # max to group values when determing direction
    TURNS_NEEDED = 5                   # turns to change directions
    DIR_CHANGE_QUEUE_LENGTH = 5        # size of dir_change queue
    CHANGE_TURN_MULTIPLIER = 1.3       # multiplier to determine if there is a turn or end of line
    ADOPT_NEW_TURN_MULTIPLIER = 0.98   # multiplier to determine when to switch the next direction to the drection
    DECREASE_TURN_MULTIPLIER = 0.8     # multiplier to determine if the value of the turn field should decrease
    
    def get_dir(self):
        """getter for direction ROV should be moving in"""
        return self.direction

    def prepare_img_red(self, video):
        """Masks image for color red and applies threshold.

        :param object video: next frame of video or camera feed to prepare for other methods
        :returns: tuple of original image and edited image 

        """

        # values to determine red color mask
        lower_bg_mask = 0
        lower_red_mask = 30
        upper_bg_mask = 70
        upper_red_mask = 255
        
        # values for gaussian blur
        blur_size = 5
        blur_sigma_x = 0

        #values for threshold
        threshold_value = 60
        threshold_max_value = 255

        retval, img = video.read()

        #arrays to determine color masks
        lower_red = np.array([lower_bg_mask, lower_bg_mask, lower_red_mask])
        upper_red = np.array([upper_bg_mask, upper_bg_mask, upper_red_mask])

        # apply masks
        mask_red = cv2.inRange(img, lower_red, upper_red)
        im_red = cv2.bitwise_and(img, img, mask=mask_red)
        im_red = cv2.GaussianBlur(im_red,(blur_size, blur_size), blur_sigma_x)

        #threshold
        ret_r, im_red = cv2.threshold(im_red, threshold_value, threshold_max_value, cv2.THRESH_BINARY)

        # flatten so findContours doesn't get mad
        im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)

        return img, im_red

    def find_start_dir(self, video):
        """Determines beginning direction when at start of line
        
        :param object video: first frame of video to determine initial direction

        """
        img, im_red = self.prepare_img_red(video)
        contours_r, hierarchy_r = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = max(contours_r, key=cv2.contourArea)
        hull = cv2.convexHull(cnt)
        (x,y), (MA,ma), angle = cv2.fitEllipse(hull)

        # determine if line is to the right or down based on the angle of the convex hull
        if(angle < self.START_ANGLE_BARRIER):
            self.direction = Direction.down
            self.next_dir = Direction.down
        else:
            self.direction = Direction.right
            self.next_dir = Direction.right

    def determine_find_dir(self, video):
        """Takes a picture and determines whether there is a turn

        :param object video: next frame of the video to determine future directions
        
        """
        img, im_red = self.prepare_img_red(video)

        # find contours
        contours_r, hierarchy_r = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours_r) > 0:
            # compute largest contour, hull, and bounding rectangle
            cnt = max(contours_r, key=cv2.contourArea)    
            x, y, w, h = cv2.boundingRect(cnt)
            hull = cv2.convexHull(cnt) 
            boundingRect = cv2.minAreaRect(hull)
            boundingRect = cv2.boxPoints(boundingRect)
            boundingRect = np.int0(boundingRect)
            hull_area = cv2.contourArea(hull)
            current_turn = cv2.contourArea(boundingRect)/hull_area
            print(self.direction)
            if self.find_turn:     # looking for turn
                self.determine_turn_type(hull, cnt, hull_area, current_turn)
            else:
                
                # determine whether there is a turn based on hull/bounding rectangle of past images in dir_change queue
                self.dir_change.append(current_turn)
                if len(self.dir_change) > self.DIR_CHANGE_QUEUE_LENGTH:
                    self.dir_change.pop(0)
                turn_avg = sum(self.dir_change)/len(self.dir_change)
                if turn_avg > self.CHANGE_TURN_MULTIPLIER * self.turn:
                    self.find_turn = True
                else:
                    # decrease the threshold to change direction if the hull/bounding rectangle ratio is decreasing
                    if turn_avg < self.ADOPT_NEW_TURN_MULTIPLIER * self.turn:
                        self.direction = self.next_dir
                    if turn_avg < self.DECREASE_TURN_MULTIPLIER * self.turn:
                        self.turn = turn_avg
                        
                #draw hull, contour, and bouding rectangle for testing purposes
                cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)
                cv2.drawContours(img, [cnt], 0, (0, 255, 0), 2)
                cv2.drawContours(img, [boundingRect], 0, (255, 0, 0), 2)
        else:
            print('No red line found')

        cv2.imshow('img', img)
        cv2.waitKey(1)

    def determine_turn_type(self, hull, cnt, hull_area, current_turn):
        """Uses the hull to find the direction of a turn

        :param numpy array hull: hull of the current turn to use to determine the next direction
        :param numpy array cnt: contour of the current turn
        :param double hull_area: area of the current turn's hull
        :param double current_turn: area of the contour bounded rectangle divided by the area of the hull
        
        """
        x_values = []
        y_values = []

        #determine if end of line reached based on contour solidity
        if (float(cv2.contourArea(cnt)) / hull_area) > self.END_OF_LINE_SOLIDITY:
           self.is_moving = False
        #group x and y values based on distance from each other
        for x in hull[:,:,0]:
           found = False
           for group in x_values:
               x_avg = sum(group)/ float(len(group))
               if x < self.MAX_GROUP_MULTIPLIER * x_avg and x > self.MIN_GROUP_MULTIPLIER * x_avg and not found:
                   group.append(x)
                   found = True 
           if not found:
               x_values.append([x])
        for y in hull[:,:,1]:
           found = False
           for group in y_values:
               y_avg = sum(group)/ float(len(group))
               if y < self.MAX_GROUP_MULTIPLIER * y_avg and y > self.MIN_GROUP_MULTIPLIER * y_avg and not found:
                   group.append(y)
                   found = True
           if not found:
               y_values.append([y])
        numBigX, numBigY, numSmallX, numSmallY = 0, 0, 0, 0
        avgBigX, avgBigY, avgSmallX, avgSmallY = 0, 0, 0, 0

        #determine top two groupings of x and y values by number of values in group
        for group in x_values:
            if len(group) > numBigX:
                numSmallX = numBigX
                avgSmallX = avgBigX
                numBigX = len(group)
                avgBigX = sum(group)/numBigX
            else:
                if len(group) > numSmallX:
                    numSmallX = len(group)
                    avgSmallX = sum(group)/numSmallX
        for group in y_values:
            if len(group) > numBigY:
                numSmallY = numBigY
                avgSmallY = avgBigY
                numBigY = len(group)
                avgBigY = sum(group)/numBigY
            else:
                if len(group) > numSmallY:
                    numSmallY = len(group)
                    avgSmallY = sum(group)/numSmallY
                    
        # determine next turn type based on average values of two biggest x and y groupings
        next_direction = Direction.neutral

        # determines next direction for down right turn
        if avgBigX < avgSmallX and avgBigY < avgSmallY:
            if self.direction == Direction.left:
                next_direction = Direction.down
            else:
               if self.direction == Direction.up:
                   next_direction = Direction.right

        # determines next direction for down left turn
        if avgBigX >  avgSmallX and avgBigY < avgSmallY:
            if self.direction == Direction.right:
                next_direction = Direction.down
            else:
                if self.direction == Direction.up:
                   next_direction = Direction.left
        # determines next direction for up left turn
        if avgBigX > avgSmallX and avgBigY > avgSmallY:
            if self.direction == Direction.right:
                next_direction = Direction.up
            else:
                if self.direction == Direction.down:
                   next_direction = Direction.left
        
        # determines next direction for up right turn
        if avgBigX < avgSmallX and avgBigY > avgSmallY:
            if self.direction == Direction.left:
                next_direction = Direction.up
            else:
                if self.direction == Direction.down:
                   next_direction = Direction.right

        # decrease the direction count if it is the same as the last direction and increment if different.
        if self.immediate_dir == next_direction and next_direction != Direction.neutral:
            self.change_dir_count -= 1
        else:
           if self.change_dir_count < self.TURNS_NEEDED:
               self.change_dir_count += 1
        if self.change_dir_count == self.TURNS_NEEDED:
           self.immediate_dir = next_direction
        # stop looking for turn if count is zero and set next direction
        if self.change_dir_count == 0:
            if self.immediate_dir != Direction.neutral:
                self.change_dir_count = self.TURNS_NEEDED 
                self.next_dir = self.immediate_dir
                self.find_turn = False
                self.turn = current_turn

if __name__ == "__main__":
    """ take a video file from command line arguments and find direction from each frame """
    cap = cv2.VideoCapture(sys.argv[1])
    follow = LineFollower()
    follow.find_start_dir(cap)
    while(follow.is_moving):
        follow.determine_find_dir(cap)
