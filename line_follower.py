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

    direction = Direction.neutral    
    immediate_dir = Direction.neutral  # currently registered direction
    next_dir = Direction.down   # will be direction when turn decreases    
    change_dir_count = 5        # number of registerd turns needed to change direction
    turn = 1000000              # threshold for average of dir_change to determine a turn
    find_turn = False           # true when program is currently determining a turn direction
    dir_change = []             # queue of bounding rect area/hull area from previous five images    
    
    def prepareImgRed(self, video):
        retval, img = video.read()
        lower_red = np.array([0, 0, 50])
        upper_red = np.array([70, 70, 255])
        lower_blue = np.array([50, 0, 0])
        upper_blue = np.array([255, 255, 255])

        # apply masks
        mask_red = cv2.inRange(img, lower_red, upper_red)
        im_red = cv2.bitwise_and(img, img, mask=mask_red)
        im_red = cv2.GaussianBlur(im_red,(5,5),0)
        # threshold
        ret_r, im_red = cv2.threshold(im_red, 60, 255, cv2.THRESH_BINARY)

        # flatten so findContours doesn't get mad
        im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)
        return img, im_red

    def findStartDir(self, video):
        img, im_red = self.prepareImgRed(video)
        contours_r, hierarchy_r = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = max(contours_r, key=cv2.contourArea)    # find largest contour

    def determineDir(self, video):
        img, im_red = self.prepareImgRed(video)

        # find contours
        contours_r, hierarchy_r = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours_r) > 0:
            cnt = max(contours_r, key=cv2.contourArea)    # find largest contour
            x, y, w, h = cv2.boundingRect(cnt)
            hull = cv2.convexHull(cnt) 
            boundingRect = cv2.minAreaRect(hull)
            boundingRect = cv2.boxPoints(boundingRect)
            boundingRect = np.int0(boundingRect)
            current_turn = cv2.contourArea(boundingRect)/cv2.contourArea(hull)
            print(self.direction)
            if self.find_turn:     # looking for turn
                 x_values = []
                 y_values = []
                 for x in hull[:,:,0]:
                    found = False
                    for group in x_values:
                        x_avg = sum(group)/ float(len(group))
                        if x < 1.4 * x_avg and x > 0.6 * x_avg and not found:
                            group.append(x)
                            found = True 
                    if not found:
                        x_values.append([x])
                 for y in hull[:,:,1]:
                    found = False
                    for group in y_values:
                        y_avg = sum(group)/ float(len(group))
                        if y < 1.4 * y_avg and y > 0.6 * y_avg and not found:
                            group.append(y)
                            found = True
                    if not found:
                        y_values.append([y])
                 numBigX, numBigY, numSmallX, numSmallY = 0, 0, 0, 0
                 avgBigX, avgBigY, avgSmallX, avgSmallY = 0, 0, 0, 0
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
                 if self.immediate_dir == next_direction:
                     self.change_dir_count -= 1
                 else:
                    if next_direction != Direction.neutral and self.change_dir_count < 5:
                        self.change_dir_count += 1
                 if self.change_dir_count == 5:
                    if next_direction != Direction.neutral:
                        self.immediate_dir = next_direction
                 if self.change_dir_count == 0:
                     self.change_dir_count = 5
                     self.next_dir = self.immediate_dir
                     self.find_turn = False
                     self.turn = current_turn
            else:
                self.dir_change.append(current_turn)
                if len(self.dir_change) > 5:
                    self.dir_change.pop(0)
                turn_avg = sum(self.dir_change)/len(self.dir_change)
                if turn_avg > 1.3 * self.turn:
                    self.find_turn = True
                else:
                    if turn_avg < 0.98 * self.turn:
                        self.direction = self.next_dir
                    if turn_avg < 0.8 * self.turn:
                        self.turn = turn_avg
            #    print("Straight line")
            # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2) 
                cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)
                cv2.drawContours(img, [boundingRect], 0, (255, 0, 0), 2)
        else:
            print('No red line found')

        cv2.imshow('img', img)
        cv2.waitKey(1)


cap = cv2.VideoCapture(sys.argv[1])
follow = LineFollower()
follow.findStartDir(cap)
while(True):
    follow.determineDir(cap)
