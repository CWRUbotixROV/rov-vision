import cv2
import numpy as np

import gi, time
from video import Video

class LineFollower:
    stream = None
    img = None
    cnt_crack = None
    found = False
    last_time = 0
    found = False

    def __init__(self, port):
        self.stream = Video(port=port)
    
    def next_direction(self):
        if not self.stream.frame_available():
            return 'invalid'
        img = self.stream.frame()

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
        ret_r, im_red = cv2.threshold(im_red, 60, 255, cv2.THRESH_BINARY)
        ret_b, im_blue = cv2.threshold(im_blue, 60, 255, cv2.THRESH_BINARY)

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
            cnt = max(contours_r, key=cv2.contourArea)    # find largest contour
            x, y, w, h = cv2.boundingRect(cnt)
            hull = cv2.convexHull(cnt)
            if cv2.contourArea(hull)/cv2.contourArea(cnt) > 2.5:     # has a bend in it
                print("Looks like a turn")
                # go_left()
            # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            else:
                print('Keep going')
                # go_down()

            # cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)
            # cv2.drawContours(img, [cnt], 0, (255, 0, 0), 2)
            if len(contours_b) > 0:
                crack = max(contours_b, key=cv2.contourArea)
                if cv2.contourArea(crack) > 1000:
                    print('Crack found!')
                    x, y, w, h = cv2.boundingRect(crack)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    self.cnt_crack = crack
                    self.found = True
        else:
            print('No red line found')

        # # Note: Showing the image makes the loop run a LOT slower
        # cv2.imshow('image', img)
        # if (cv2.waitKey(1) & 0xFF == ord('q')) or self.found:
        #     return 'end'
