import cv2
import numpy as np
import math

class GridMap:
    x = 0
    y = 0
    hlines = []
    vlines = []
    thresh = 50

    def update(self, image):
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 0, 0])
        upper = np.array([180, 50, 150])
        mask = cv2.inRange(hsv, lower, upper)

        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5)

        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 50, None, 50, 10)

        height, width, channels = image.shape
        horizontal = []
        vertical = []

        #Sort lines by horizontal and vertical
        if lines is not None:
            for i in range(0, len(lines)):
                l = lines[i][0]
                if (l[2] != l[0]):
                    m = (l[3] - l[1]) / (l[2] - l[0])
                    if (m > -0.5 and m < 0.5):
                        y = ((width / 2) - l[0]) * m + l[1]
                        horizontal.append(y)
                    elif (m < -2 or m > 2):
                        x = ((height / 2) - l[1]) * (1 / m) + l[0]
                        vertical.append(x)
                #cv2.line(image, (l[0], l[1]), (l[2], l[3]), (0,255,0), 3, cv2.LINE_AA)

        #Sort lines and group
        horizontal.sort()
        sum = 0
        count = 0
        havg = []

        if len(horizontal) > 0:
            for i in range(0, len(horizontal) - 1):
                sum += horizontal[i]
                count += 1
                if (horizontal[i + 1] - horizontal[i] > self.thresh):
                    avg = sum / count
                    havg.append(avg)
                    sum = 0
                    count = 0
            sum += horizontal[len(horizontal) - 1]
            count += 1
            avg = sum / count
            havg.append(avg)
        

        vertical.sort()
        sum = 0
        count = 0
        vavg = []

        if len(vertical) > 0:
            for i in range(0, len(vertical) - 1):
                sum += vertical[i]
                count += 1
                if (vertical[i + 1] - vertical[i] > self.thresh):
                    avg = sum / count
                    vavg.append(avg)
                    sum = 0
                    count = 0
            sum += vertical[len(vertical) - 1]
            count += 1
            avg = sum / count
            vavg.append(avg)
        

        #Update lines
        # for y in havg:
        #     cv2.line(image, (0, int(y)), (10000, int(y)), (0,255,0), 3, cv2.LINE_AA)
        #     update = False
        #     for line in self.hlines:
        #         if (abs(line[0] - y) < thresh):
        #             line[0] = y
        #             line[1] += 1
        #             update = True
        #     if (update == False):
        #         self.hlines.append([y, 0])
        # for x in vavg:
        #     cv2.line(image, (int(x), 0), (int(x), 10000), (0,255,0), 3, cv2.LINE_AA)

        #Update lines
        for y in havg:
            cv2.line(image, (0, int(y)), (10000, int(y)), (0,255,0), 3, cv2.LINE_AA)
            update = False
            for line in self.hlines:
                if (line.update(y)):
                    update = True
                elif (line.unupdated > 5):
                    self.hlines.remove(line)
            if (update == False):
                self.hlines.append(Line(y, 500))

        # lines = cv2.HoughLines(mask, 1, np.pi / 180, 300, None, 0, 0)
        # if lines is not None:
        #     for i in range(0, len(lines)):
        #         rho = lines[i][0][0]
        #         theta = lines[i][0][1]
        #         a = math.cos(theta)
        #         b = math.sin(theta)
        #         x0 = a * rho
        #         y0 = b * rho
        #         pt1 = (int(x0 + 10000*(-b)), int(y0 + 10000*(a)))
        #         pt2 = (int(x0 - 10000*(-b)), int(y0 - 10000*(a)))
        #         cv2.line(image, pt1, pt2, (0,255,0), 3, cv2.LINE_AA)

        cv2.imshow("test", image)
        cv2.waitKey(1)


class Line:
    thresh = 50
    def __init__(self, pos, bound):
        self.pos = pos
        self.duration = 1
        self.unupdated = 0
        self.bound = bound
        self.crossed = 0
        self.counted = False
        self.start = pos
    
    def update(self, pos):
        if (abs(self.pos - pos) < self.thresh):
            
            if (self.duration > 5 and self.crossed == 0):
                if (pos >= self.bound and self.pos < self.bound):
                    self.crossed = 1
                elif (pos <= self.bound and self.pos > self.bound):
                    self.crossed = -1

            self.pos = pos
            self.duration += 1


            return True
        else:
            self.unupdated += 1
            return False



video = cv2.VideoCapture("/home/vm/Downloads/line_follow3.mp4")
map = GridMap()
while (True):
    retval, image = video.read()
    map.update(image)
