import cv2
import numpy as np
from enum import Enum

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
    turn = 100
    find_turn = True
    
    def determineDir(self, video):
        retval, img = video.read()
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
            current_turn = cv2.contourArea(hull)/cv2.contourArea(cnt)
            if self.find_turn:     # has a bend in it
                # print("Looks like a turn")
                 lines = cv2.HoughLinesP(im_red, 1, np.pi/180, 200, 20, 20)
                 x_values = []
                 y_values = []
                 for line in lines:
                    for x1,y1,x2,y2 in line:
                        for group in x_values:
                            x_avg = sum(group)/ float(len(group))
                            if x1 < 1.2 * x_avg and x1 > 0.8 * x_avg:
                                group.append(x1)
                                break
                        else:
                            x_values.append([x2])
                        for group in x_values:
                            x_avg = sum(group)/ float(len(group))
                            if x2 < 1.2 * x_avg and x2 > 0.8 * x_avg:
                                group.append(x1)
                                break
                        else:
                            x_values.append([x2])
                        for group in y_values:
                            y_avg = sum(group)/ float(len(group))
                            if y1 < 1.2 * y_avg and y1 > 0.8 * y_avg:
                                group.append(y1)
                                break
                        else:
                            y_values.append([y1])
                        for group in y_values:
                            y_avg = sum(group)/ float(len(group))
                            if y2 < 1.2 * x_avg and y2 > 0.8 * x_avg:
                                group.append(y2)
                                break
                        else:
                            y_values.append([y2])
                        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
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
                         if self.direction == Direction.up:
                            next_direction = Direction.up
                 if self.immediate_dir == next_direction:
                     self.change_dir_count -= 1
                 if next_direction != Direction.neutral:
                     self.immediate_dir = next_direction
                 if self.change_dir_count == 0:
                     self.change_dir_count = 5
                     self.direction = self.immediate_dir
                     self.find_turn = False
                     self.turn = current_turn
                 print(self.direction)
            else:
                if current_turn > 1.8 * self.turn:
                    self.find_turn = True
                else:
                    if current_turn < 0.8 * self.turn:
                        self.turn = current_turn
            #    print("Straight line")
            # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2) 
                cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)
                cv2.drawContours(img, [cnt], 0, (255, 0, 0), 2)

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

        cv2.imshow('image', img)
        cv2.waitKey(10)


cap = cv2.VideoCapture(0)
follow = LineFollower()
while(True):
    follow.determineDir(cap)
