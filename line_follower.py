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

    direction = Direction.down
    immediate_dir = Direction.down
    change_dir_count = 5
    turn = 1000000
    find_turn = False
    dir_change = []
    
    def determineDir(self, video):
        retval, img = video.read()
        lower_red = np.array([0, 0, 100])
        upper_red = np.array([60, 60, 255])
        lower_blue = np.array([50, 0, 0])
        upper_blue = np.array([255, 255, 255])

        # apply masks
        mask_red = cv2.inRange(img, lower_red, upper_red)
        mask_blue = cv2.inRange(img, lower_blue, upper_blue)
        im_red = cv2.bitwise_and(img, img, mask=mask_red)
        im_blue = cv2.bitwise_and(img, img, mask=mask_blue)
        im_red = cv2.GaussianBlur(im_red,(5,5),0)
        # threshold
        ret_r, im_red = cv2.threshold(im_red, 60, 255, cv2.THRESH_BINARY)
        ret_b, im_blue = cv2.threshold(im_blue, 60, 255, cv2.THRESH_BINARY)

        # flatten so findContours doesn't get mad
        im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)
        im_blue = cv2.cvtColor(im_blue, cv2.COLOR_BGR2GRAY)

        # find contours
        contours_r, hierarchy_r = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_b, hierarchy_b = cv2.findContours(im_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours_r) > 0:
            cnt = max(contours_r, key=cv2.contourArea)    # find largest contour
            x, y, w, h = cv2.boundingRect(cnt)
            hull = cv2.convexHull(cnt) 
            boundingRect = cv2.minAreaRect(hull)
            boundingRect = cv2.boxPoints(boundingRect)
            boundingRect = np.int0(boundingRect)
            current_turn = cv2.contourArea(boundingRect)/cv2.contourArea(hull)
            print(self.direction)
            if self.find_turn:     # has a bend in it
                # print("Looks like a turn")
                 lines = cv2.HoughLinesP(im_red, 1, np.pi/180, 500, 100, 20)
                 x_values = []
                 y_values = []
                 for line in lines:
                    for x1,y1,x2,y2 in line:
                        found1 = False
                        found2 = False
                        for group in x_values:
                            x_avg = sum(group)/ float(len(group))
                            if x1 < 1.2 * x_avg and x1 > 0.8 * x_avg and not found1:
                                group.append(x1)
                                found1 = True 
                            if x2 < 1.2 * x_avg and x2 > 0.8 * x_avg and not found2:
                                group.append(x2)
                                found2 = True
                            if found1 and found2:
                                break
                        if not found1:
                            x_values.append([x1])
                        if not found2:
                            x_values.append([x2])
                        found1 = False
                        found2 = False
                        for group in y_values:
                            y_avg = sum(group)/ float(len(group))
                            if y1 < 1.2 * y_avg and y1 > 0.8 * y_avg and not found1:
                                group.append(y1)
                                found1 = True
                            if y2 < 1.2 * y_avg and y2 > 0.8 * y_avg and not found2:
                                group.append(y2)
                                found2 = True
                            if found1 and found2:
                                break
                        if not found1:
                            y_values.append([y1])
                        if not found2:
                            y_values.append([y2])
                        # cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
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
                     self.direction = self.immediate_dir
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
                    if turn_avg < 0.8 * self.turn:
                        self.turn = turn_avg
            #    print("Straight line")
            # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2) 
                cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)
                cv2.drawContours(img, [boundingRect], 0, (255, 0, 0), 2)
            if len(contours_b) > 0:
                crack = max(contours_b, key=cv2.contourArea)
                # if cv2.contourArea(crack) > 1000:
                #     print('Crack found!')
                #     x, y, w, h = cv2.boundingRect(crack)
                #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                #     cnt_crack = crack
                #     found = True
        else:
            print('No red line found')

        #cv2.imshow('img', img)
        cv2.waitKey(1)


cap = cv2.VideoCapture(sys.argv[1])
follow = LineFollower()
while(True):
    follow.determineDir(cap)
