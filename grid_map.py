import cv2, imutils
import numpy as np
import math
import measurecrack
from line_follower_2 import LineFollower, Direction
import colors

class GridMap:
    hlines = []
    vlines = []
    thresh = 300
    crackx = 0
    cracky = 0
    maxblueratio = 0

    def __init__(self, startframe):
        pass
        # lf = LineFollower()
        # lf.find_start_dir(startframe)
        # if (lf.direction == Direction.down):
        #     self.x = 0
        #     self.y = -1
        # else:
        #     self.x = -1
        #     self.y = 0
        


    def update(self, image):
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        LOWER = np.array([0, 0, 0])
        UPPER = np.array([180, 100, 110])
        mask = cv2.inRange(hsv, LOWER, UPPER)

        thresh = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 7, 4)
        resized = imutils.resize(thresh, width=800)
        cv2.imshow('image', resized)
        cv2.waitKey(0)

        mask = colors.getMask("black", image)
        resized = imutils.resize(mask, width=800)
        cv2.imshow('image', resized)
        cv2.waitKey(0)

        kernel = np.ones((11, 11), np.uint8)
        eroded = cv2.erode(mask, kernel)
        resized = imutils.resize(eroded, width=800)
        cv2.imshow('image', resized)
        cv2.waitKey(0)

        threshAndMask = cv2.bitwise_and(thresh, eroded)
        resized = imutils.resize(threshAndMask, width=800)
        cv2.imshow('image', resized)
        cv2.waitKey(0)

        # Detect Lines
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 50, None, 50, 10)

        height, width, channels = image.shape
        horizontal = []
        vertical = []

        HORIZONTAL_THRESH = 0.5
        VERTICAL_THRESH = 2

        #Sort lines by horizontal and vertical
        if lines is not None:
            for i in range(0, len(lines)):
                l = lines[i][0]
                if (l[2] != l[0]):
                    m = (l[3] - l[1]) / (l[2] - l[0])
                    if (m > -HORIZONTAL_THRESH and m < HORIZONTAL_THRESH):
                        y = ((width / 2) - l[0]) * m + l[1]
                        horizontal.append(y)
                    elif (m < -VERTICAL_THRESH or m > VERTICAL_THRESH):
                        x = ((height / 2) - l[1]) * (1 / m) + l[0]
                        vertical.append(x)

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
        
        # Sort lines
        vertical.sort()
        sum = 0
        count = 0
        vavg = []

        # Group vertical lines that are close together into vavg
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

        # Update horizontal and vertical lines with new coordinates
        updateLines(havg, self.hlines, height / 2)
        updateLines(vavg, self.vlines, width / 2)

        # Check if any horizontal lines have crossed
        for line in self.hlines:
            if (line.counted == False and line.crossed != 0):
                self.y += line.crossed
                line.counted = True
            y = line.pos
            #cv2.line(image, (0, int(y)), (10000, int(y)), (0,255,0), 3, cv2.LINE_AA)

        # Check if any vertical lines have crossed
        for line in self.vlines:
            if (line.counted == False and line.crossed != 0):
                self.x += line.crossed
                line.counted = True
            x = line.pos
            #cv2.line(image, (int(x), 0), (int(x), 10000), (0, 255, 0), 3, cv2.LINE_AA)

        # Find the ratio of the image that is blue
        blueratio = blueRectangle(image)
        # If the blue ratio is bigger than the max and current position is within bounds then update the location of the blue crack
        if (blueratio > self.maxblueratio and self.x >= 0 and self.x <=3 and self.y >=0 and self.y <=2):
            self.maxblueratio = blueratio
            self.crackimage = image
            self.crackx = self.x
            self.cracky = self.y

        if (self. x == 4 or self.y == 3 or (self.x == 3 and self.y == -1)):
            cv2.imshow("blue", self.crackimage)
            cv2.waitKey(0)
            displayCrack(self.crackx, self.cracky, self.crackimage)

        resized = imutils.resize(mask, width=800)

        cv2.imshow("mask", resized)
        cv2.waitKey(1)

        resized = imutils.resize(image, width=800)

        cv2.imshow("image", resized)
        cv2.waitKey(0)

def updateLines(newLines, lines, half):
    # Check each coordinate against each existing line
    for coordinate in newLines:
        update = False
        for line in lines:
            if (line.update(coordinate)):
                update = True
                break
        # If a coordinate does not correspond to any existing line, create a new line
        if (update == False):
            lines.append(Line(coordinate, half))
    # Check to see which lines have not updated with any of the new coordinates
    REMOVE_THRESH = 5
    for line in lines:
        if (line.updated == False):
            line.unupdated += 1
            # If a line has not been updated, remove it
            if (line.unupdated > REMOVE_THRESH):
                lines.remove(line)
        else:
            line.updated = False


class Line:
    thresh = 300
    def __init__(self, pos, bound):
        self.pos = pos
        self.duration = 1
        self.unupdated = 0
        self.updated = False
        self.bound = bound
        self.crossed = 0
        self.counted = False
    
    def update(self, pos):
        '''Checks if the line is close to the new coordinate and returns true if it updates'''
        # Check if coordinate is within threshold of current position
        if (abs(self.pos - pos) < self.thresh):
            # If it has not crossed yet, check to see it crosses on this update
            if (self.duration > 0 and self.crossed == 0):
                if (pos >= self.bound and self.pos < self.bound):
                    self.crossed = -1
                elif (pos <= self.bound and self.pos > self.bound):
                    self.crossed = 1
            # Update position and updated status
            self.pos = pos
            self.duration += 1
            self.updated = True

            return True
        else:
            return False

def blueRectangle(image):
    '''Returns ratio of the image that is blue'''

    # Mask blue colors
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


def displayCrack(x, y, crackimage):
    '''Displays the length of the crack in the square at x, y'''
    CELL_SIZE = 200
    PADDING = 20
    HEIGHT = CELL_SIZE * 3 + (2 * PADDING)
    WIDTH = CELL_SIZE * 4 + (2 * PADDING)
    THICKNESS = 2

    # Create white image
    image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    cv2.rectangle(image, (0, 0), (WIDTH, HEIGHT), (255, 255, 255), -1)

    # Draw grid
    for n in range(5):
        cv2.line(image, (CELL_SIZE * n + PADDING, PADDING), (CELL_SIZE * n + PADDING, CELL_SIZE * 3 + PADDING), (0, 0, 0), THICKNESS)
    for n in range(4):
        cv2.line(image, (PADDING, CELL_SIZE * n + PADDING), (CELL_SIZE * 4 + PADDING, CELL_SIZE * n + PADDING), (0, 0, 0), THICKNESS)

    # Find length
    cv2.imwrite("test.png", crackimage)
    length = measurecrack.measureCrackPerspective(crackimage)
    # Round length
    length = round(length, 1)

    # Write text
    cv2.putText(image, str(length) + " cm", (int(CELL_SIZE * (x + 0.2) + PADDING), int(CELL_SIZE * (y + 0.5) + PADDING)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), THICKNESS)

    cv2.imshow("Crack map", image)
    cv2.waitKey(0)


image = cv2.imread("calibrate.png")
map = GridMap(image)
map.update(image)

video = cv2.VideoCapture("/home/vm/Downloads/line.mp4")
retval, image = video.read()
map = GridMap(image)
#video.set(cv2.CAP_PROP_POS_FRAMES, 780)
#displayCrack(2, 2, 13.672)
while (True):
    retval, image = video.read()
    map.update(image)
    print(str(map.x) + " " + str(map.y))
