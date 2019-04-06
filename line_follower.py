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

    direction = Direction.neutral      # direction the ROV should move in to follow line
    immediate_dir = Direction.neutral  # currently registered direction
    next_dir = Direction.neutral       # will be direction when turn decreases    
    change_dir_count = 5               # number of registerd turns needed until direction changes
    turn = 1000000                     # threshold for average of dir_change to determine a turn
    find_turn = False                  # true when program is currently determining a turn direction
    dir_change = []                    # queue of bounding rect area/hull area from previous five images    
    is_moving = True                   # determines when line_following stops


    start_angle_barrier = 45           # barrier angle for whether line start it to the right or down
    end_of_line_solidity = 0.7         # solidity determine end of line
    min_group_multiplier = 0.8         # min to group values when determing direction
    max_group_multiplier = 1.2         # max to group values when determing direction
    turns_needed = 5                   # turns to change directions
    dir_change_queue_length = 5        # size of dir_change queue
    change_turn_multiplier = 1.3        # multiplier to determine if there is a turn or end of line
    adopt_new_turn_multiplier = 0.98   # multiplier to determine when to switch the next direction to the drection
    decrease_turn_multiplier = 0.8     # multiplier to determine if the value of the turn field should decrease
    
    def prepareImgRed(self, video):

        retval, img = video.read()

        #arrays to determine color masks
        lower_red = np.array([0, 0, 30])
        upper_red = np.array([70, 70, 255])
        lower_blue = np.array([50, 0, 0])
        upper_blue = np.array([255, 255, 255])

        # apply masks
        mask_red = cv2.inRange(img, lower_red, upper_red)
        im_red = cv2.bitwise_and(img, img, mask=mask_red)
        im_red = cv2.GaussianBlur(im_red,(5,5),0)
        #threshold
        ret_r, im_red = cv2.threshold(im_red, 60, 255, cv2.THRESH_BINARY)

        # flatten so findContours doesn't get mad
        im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)

        return img, im_red

    def getDir(self):
        return self.direction

    def findStartDir(self, video):
        img, im_red = self.prepareImgRed(video)
        contours_r, hierarchy_r = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = max(contours_r, key=cv2.contourArea)
        hull = cv2.convexHull(cnt)
        (x,y), (MA,ma), angle = cv2.fitEllipse(hull)

        # determine if line is to the right or down based on the angle of the convex hull
        if(angle < self.start_angle_barrier):
            self.direction = Direction.down
            self.next_dir = Direction.down
        else:
            self.direction = Direction.right
            self.next_dir = Direction.right

    def determineDir(self, video):
        img, im_red = self.prepareImgRed(video)

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
            hullArea = cv2.contourArea(hull)
            current_turn = cv2.contourArea(boundingRect)/hullArea
            print(self.direction)
            if self.find_turn:     # looking for turn
                 x_values = []
                 y_values = []

                 #determine if end of line reached based on contour solidity
                 if (float(cv2.contourArea(cnt)) / hullArea) > self.end_of_line_solidity:
                    self.is_moving = False
                 #group x and y values based on distance from each other
                 for x in hull[:,:,0]:
                    found = False
                    for group in x_values:
                        x_avg = sum(group)/ float(len(group))
                        if x < self.max_group_multiplier * x_avg and x > self.min_group_multiplier * x_avg and not found:
                            group.append(x)
                            found = True 
                    if not found:
                        x_values.append([x])
                 for y in hull[:,:,1]:
                    found = False
                    for group in y_values:
                        y_avg = sum(group)/ float(len(group))
                        if y < self.max_group_multiplier * y_avg and y > self.min_group_multiplier * y_avg and not found:
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
                             
                #determine next direction based on average values of two biggest x and y groupings
                 next_direction = Direction.neutral
                 if avgBigX < avgSmallX and avgBigY < avgSmallY:
                     if self.direction == Direction.left:
                         next_direction = Direction.down
                     else:
                         if self.direction == Direction.up:
                            next_direction = Direction.right

                 if avgBigX >  avgSmallX and avgBigY < avgSmallY:
                     if self.direction == Direction.right:
                         next_direction = Direction.down
                     else:
                         if self.direction == Direction.up:
                            next_direction = Direction.left
                 
                 if avgBigX > avgSmallX and avgBigY > avgSmallY:
                     if self.direction == Direction.right:
                         next_direction = Direction.up
                     else:
                         if self.direction == Direction.down:
                            next_direction = Direction.left
                 
                 if avgBigX < avgSmallX and avgBigY > avgSmallY:
                     if self.direction == Direction.left:
                         next_direction = Direction.up
                     else:
                         if self.direction == Direction.down:
                            next_direction = Direction.right

                 # change the count based on found direction and change direction if count equals zero
                 if self.immediate_dir == next_direction and next_direction != Direction.neutral:
                     self.change_dir_count -= 1
                 else:
                    if self.change_dir_count < self.turns_needed:
                        self.change_dir_count += 1
                 if self.change_dir_count == self.turns_needed:
                    self.immediate_dir = next_direction
                 if self.change_dir_count == 0:
                     if self.immediate_dir != Direction.neutral:
                         self.change_dir_count = self.turns_needed 
                         self.next_dir = self.immediate_dir
                         self.find_turn = False
                         self.turn = current_turn
            else:
                
                # determine whether there is a turn based on hull/bounding rectabgle of past few images
                self.dir_change.append(current_turn)
                if len(self.dir_change) > self.dir_change_queue_length:
                    self.dir_change.pop(0)
                turn_avg = sum(self.dir_change)/len(self.dir_change)
                if turn_avg > self.change_turn_multiplier * self.turn:
                    self.find_turn = True
                else:
                    if turn_avg < self.adopt_new_turn_multiplier * self.turn:
                        self.direction = self.next_dir
                    if turn_avg < self.decrease_turn_multiplier * self.turn:
                        self.turn = turn_avg
                        
                #draw hull, contour, and bouding rectangle for testing purposes
                cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)
                cv2.drawContours(img, [cnt], 0, (0, 255, 0), 2)
                cv2.drawContours(img, [boundingRect], 0, (255, 0, 0), 2)
        else:
            print('No red line found')

        cv2.imshow('img', img)
        cv2.waitKey(1)


cap = cv2.VideoCapture(sys.argv[1])
follow = LineFollower()
follow.findStartDir(cap)
while(follow.is_moving):
    follow.determineDir(cap)
