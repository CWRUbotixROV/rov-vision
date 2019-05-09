import cv2, imutils
import numpy as np
import math

class GridMap:
    hlines = []
    vlines = []
    thresh = 200
    crackx = 0
    cracky = 0
    maxblueratio = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, image):
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        LOWER = np.array([60, 0, 0])
        UPPER = np.array([130, 255, 45])
        mask = cv2.inRange(hsv, LOWER, UPPER)

        LOWER = np.array([0, 14, 9])
        UPPER = np.array([2, 25, 17])
        mask = cv2.inRange(blurred, LOWER, UPPER)

        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5)

        # Detect Lines
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

        #Sort lines
        horizontal.sort()
        sum = 0
        count = 0
        havg = []

        # Group horizontal lines that are close together into havg
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
        
        # Group vertical lines that are close together into vavg
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
            cv2.line(image, (0, int(y)), (10000, int(y)), (255,0,0), 3, cv2.LINE_AA)
        #     update = False
        #     for line in self.hlines:
        #         if (line.update(y)):
        #             update = True
        #         elif (line.unupdated > 5):
        #             self.hlines.remove(line)
        #     if (update == False):
        #         self.hlines.append(Line(y, 500))

        updateLines(havg, self.hlines, height / 2)
        updateLines(vavg, self.vlines, width / 2)

        # Check if any horizontal lines have crossed
        for line in self.hlines:
            if (line.counted == False and line.crossed != 0):
                self.y += line.crossed
                line.counted = True
            y = line.pos
            cv2.line(image, (0, int(y)), (10000, int(y)), (0,255,0), 3, cv2.LINE_AA)

        # Check if any vertical lines have crossed
        for line in self.vlines:
            if (line.counted == False and line.crossed != 0):
                self.x += line.crossed
                line.counted = True
            x = line.pos
            cv2.line(image, (int(x), 0), (int(x), 10000), (0, 255, 0), 3, cv2.LINE_AA)

        # Find the ratio of the image that is blue
        blueratio = blueRectangle(image)
        # If the blue ratio is bigger than the max then update the location of the blue crack
        if (blueratio > self.maxblueratio):
            self.maxblueratio = blueratio
            self.crackx = self.x
            self.cracky = self.y

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

        resized = imutils.resize(mask, width=800)

        cv2.imshow("mask", resized)
        cv2.waitKey(1)

        resized = imutils.resize(image, width=800)

        cv2.imshow("image", resized)
        cv2.waitKey(1)

def updateLines(newLines, lines, half):
    for coordinate in newLines:
        update = False
        for line in lines:
            if (line.update(coordinate)):
                update = True
                break
        if (update == False):
            lines.append(Line(coordinate, half))
    for line in lines:
        if (line.updated == False):
            line.unupdated += 1
            if (line.unupdated > 5):
                lines.remove(line)
        else:
            line.updated = False


class Line:
    thresh = 200
    def __init__(self, pos, bound):
        self.pos = pos
        self.duration = 1
        self.unupdated = 0
        self.updated = False
        self.bound = bound
        self.crossed = 0
        self.counted = False
        self.start = pos
    
    def update(self, pos):
        if (abs(self.pos - pos) < self.thresh):
            
            if (self.duration > 0 and self.crossed == 0):
                if (pos >= self.bound and self.pos < self.bound):
                    self.crossed = -1
                    print("-1")
                elif (pos <= self.bound and self.pos > self.bound):
                    self.crossed = 1
                    print("1")

            self.pos = pos
            self.duration += 1
            self.updated = True

            return True
        else:
            return False

def blueRectangle(image):
    #hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    LOWER_BLUE = np.array([0, 0, 0])
    UPPER_BLUE = np.array([255, 80, 80])
    mask = cv2.inRange(image, LOWER_BLUE, UPPER_BLUE)

    sum = cv2.sumElems(mask)[0] / 255

    height, width, channels = image.shape
    total = height * width
    return sum / total

    # resized = imutils.resize(mask, width=800)

    # cv2.imshow("test", resized)
    # cv2.waitKey(1)


def displayCrack(x, y, length):
    CELL_SIZE = 200
    PADDING = 20
    HEIGHT = CELL_SIZE * 3 + (2 * PADDING)
    WIDTH = CELL_SIZE * 4 + (2 * PADDING)
    THICKNESS = 3

    # Create white image
    image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    cv2.rectangle(image, (0, 0), (WIDTH, HEIGHT), (255, 255, 255), -1)

    # Draw grid
    for n in range(5):
        cv2.line(image, (CELL_SIZE * n + PADDING, PADDING), (CELL_SIZE * n + PADDING, CELL_SIZE * 3 + PADDING), (0, 0, 0), THICKNESS)
    for n in range(4):
        cv2.line(image, (PADDING, CELL_SIZE * n + PADDING), (CELL_SIZE * 4 + PADDING, CELL_SIZE * n + PADDING), (0, 0, 0), THICKNESS)

    # Write text
    cv2.putText(image, str(length) + " cm", (int(CELL_SIZE * (x + 0.3) + PADDING), int(CELL_SIZE * (y + 0.5) + PADDING)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), THICKNESS)

    cv2.imshow("Crack map", image)
    cv2.waitKey(0)

video = cv2.VideoCapture("/home/vm/Downloads/underwater.mp4")
map = GridMap(0, 0)
#video.set(cv2.CAP_PROP_POS_FRAMES, 700)
#displayCrack(2, 1, 13.6)
while (True):
    retval, image = video.read()
    map.update(image)
    print(str(map.x) + " " + str(map.y))
