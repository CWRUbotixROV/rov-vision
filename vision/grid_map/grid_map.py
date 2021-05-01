"""Contains methods to map video with lines from a mask"""

from vision.images import *
from vision.grid_map.grid_square import *
import cv2
import numpy as np

# Runs grid mapping methods
class GridMapper:
    def __init__(self):
        self.id = 0  # Unique ID for each square
        self.squares = []  # Tracks square objects on the current frame
        self.all_squares = []  # All detected squares in the video
        self.images = []  # Screenshots of all squares
        self.frame_area = 0

        # For final grid image
        self.cell_size = 150  # Size of each cell
        self.padding = 8  # Line thickness
        self.cell_coords = []  # Coordinates for each cell

    def draw_lines(self, frame, mask):
        """Draws HoughLines on image
        For example: 'draw_lines(frame, edges)'"""
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=400)

        if lines is not None:
            for i in range(len(lines)):
                line = lines[i]

                x1, y1, x2, y2 = line.reshape(4)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    def update_frame(self, frame):
        contrast = cv2.addWeighted(frame, 1.5, np.zeros(frame.shape, frame.dtype), 0, 0)

        hsv = cv2.cvtColor(contrast, cv2.COLOR_BGR2HSV)

        lower_red = np.array([150, 10, 0])
        upper_red = np.array([179, 100, 255])

        lower_blue = np.array([30, 100, 50])
        upper_blue = np.array([130, 255, 255])

        lower_yellow = np.array([25, 100, 50])
        upper_yellow = np.array([50, 255, 255])

        red_mask = cv2.inRange(hsv, lower_red, upper_red)
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        mask = red_mask + blue_mask + yellow_mask

        ksize = 7
        blur = cv2.GaussianBlur(mask, (ksize, ksize), 1)

        thresh1 = cv2.getTrackbarPos("Thresh1", "Trackbar")
        thresh2 = cv2.getTrackbarPos("Thresh2", "Trackbar")

        canny = cv2.Canny(blur, thresh1, thresh2)

        lines = np.zeros_like(frame)
        self.draw_lines(lines, canny)

        ksize2 = 10
        kernel = np.ones((ksize2, ksize2))
        lines = cv2.dilate(lines, kernel, iterations=1)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        contours = self.get_contours(lines, frame)
        self.find_squares(contours, frame)

        show_debug(frame, name="frame", wait=False)
        # show_debug(lines, name="lines", wait=False)

        return

    def get_contours(self, mask, frame):
        """Detects squares by analyzing the contours of the frame"""

        curr_squares = []  # Squares in the current frame
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, .01 * cv2.arcLength(cnt, True), True)

            if self.frame_area * .03 < area < self.frame_area * .25:
                # cv2.drawContours(frame, [approx], 0, (255, 0, 0), 5)

                # Check if the contour has 4 sides
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)

                    # Check if sides are equal-ish lengths
                    dim_error = (abs(w - h)/w)  # Error between width and height

                    if dim_error < .2:
                        curr_squares.append(Square(x, y, w, h))

        return curr_squares

    def find_squares(self, curr_squares, frame):
        """Tracks squares and assigns a unique ID to each square"""

        squares = self.squares  # Square objects already being tracked
        all_squares = self.all_squares
        matched = []  # id of squares in curr_squares matched to a square in squares

        # Check if a square should be tracked or deleted
        if len(squares) == 0:
            for s in curr_squares:
                self.id += 1
                s.id = self.id
                squares.append(s)
                matched.append(s)

        else:
            for s in squares:
                s.visible = False

            for s1 in curr_squares:
                for s2 in squares:
                    # If a detected square is similar to a square already being tracked, update the square's info
                    if np.allclose([s1.x, s1.y, s1.w, s1.h], [s2.x, s2.y, s2.w, s2.h], atol=100):
                        s2.x = s1.x
                        s2.y = s1.y
                        s2.w = s1.w
                        s2.h = s1.h

                        s1.id = s2.id
                        matched.append(s1.id)

                        s2.visible = True
                        s2.delete = 0
                        break

        # Only call find neighbors if there are new squares on the screen
        find_neighbors = False

        for s in squares:
            if s not in all_squares:
                # Adding squares to all squares if they haven't been added
                all_squares.append(s)

                if not find_neighbors:
                    self.find_neighbors()
                    find_neighbors = True

        # If a square is not visible for 20 consecutive frames, delete it
        for s in squares:
            if not s.visible:
                if s.delete == 20:
                    squares.remove(s)
                else:
                    s.delete += 1

        if len(curr_squares) != len(matched):
            for s in curr_squares:
                if s.id not in matched:
                    self.id += 1
                    s.id = self.id
                    matched.append(s.id)
                    squares.append(s)

        self.screenshot_squares(frame)

        # Drawing squares on the frame in debug mode
        if config.debug:
            for s in squares:
                if s.visible:
                    cv2.putText(frame, str(s.id), (s.x + int(s.w / 2), s.y + int(s.w / 2)),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
                    cv2.rectangle(frame, (s.x, s.y), (s.x + s.w, s.y + s.h), (0, 255, 0), 5)

    def find_neighbors(self):
        """Finds neighboring squares (4 square neighborhood)"""

        for i in range(0, len(self.squares)):
            s = self.squares[i]

            # print(f"ID: {s.id}, x: {s.x}, y: {s.y}")

            for j in range(0, len(self.squares)):
                s2 = self.squares[j]

                # print(f"ID2: {s2.id}, x: {s2.x}, y: {s2.y}")

                if s != s2:
                    xdiff = s.x - s2.x
                    ydiff = s.y - s2.y

                    # Values must be within these tolerances to be neighbors
                    tol = s.w * 1.4
                    tol2 = 10

                    # Check left and right
                    if s.left is None or s.right is None:
                        if abs(xdiff) <= tol and abs(ydiff) <= tol2:
                            # s2 is to the left of s1
                            if xdiff > 0:
                                s.left = s2

                            # s2 is to the right of s1
                            else:
                                s.right = s2

                    # Check up and down
                    if s.up is None or s.down is None:
                        if abs(ydiff) <= tol and abs(xdiff) <= tol2:
                            # s2 is above s1
                            if ydiff > 0:
                                s.up = s2

                            # s2 is below s1
                            else:
                                s.down = s2

    def screenshot_squares(self, frame):
        """Screenshots each square"""

        for s in self.squares:
            if s.screenshot_num != 5:
                s.screenshot_num += 1

                roi = frame[s.y:s.y + s.h, s.x:s.x + s.w]
                self.images.append(Screenshot(s.id, roi))

    def create_grid_squares(self):
        """Creates Grid_Square objects for object detection"""
        all_grid_squares = []  # Contains all Grid_Square objects

        # Creating 27 Grid_Squares
        for i in range(27):
            all_grid_squares.append(Grid_Square(i + 1))

        # Adding screenshots to the Grid_Squares
        for i in range(len(self.images)):
            screenshot = self.images[i]
            all_grid_squares[screenshot.id - 1].images.append(screenshot.image)

        return all_grid_squares

    def map_squares(self):
        left = []
        middle = []
        right = []

        empty_square = Square(None, None, None, None)

        top_left = empty_square
        top_middle = empty_square
        top_right = empty_square

        map = [[empty_square] * 3 for i in range(9)]

        for s in self.all_squares:
            if s.left is None:
                left.append(s)

                if s.up is None:
                    top_left = s

            elif s.right is None:
                right.append(s)

                if s.up is None:
                    top_middle = s

            else:
                middle.append(s)

                if s.up is None:
                    top_right = s

        # Sorting lists numerically by square id
        left = sorted(left, key=lambda x: x.id)
        middle = sorted(middle, key=lambda x: x.id)
        right = sorted(right, key=lambda x: x.id)

    def display_grid(self, all_grid_squares):
        """Displays the final grid"""

        border = 100  # Border around grid
        width = 3 * self.cell_size + 4 * self.padding  # width of window
        height = 9 * self.cell_size + 10 * self.padding  # height of window

        img = np.zeros((height + 2 * border, width + 2 * border, 3), dtype=np.uint8)
        img.fill(255)

        # Draw vertical grid lines
        start_x = border + self.padding
        start_y = start_x

        for i in range(4):
            cv2.line(img, (start_x, start_y), (start_x, height + border), (0, 0, 0), self.padding, 1)
            start_x += self.cell_size + self.padding

        # Draw horizontal grid lines
        start_x = border + self.padding  # Reset x position

        for i in range(10):
            cv2.line(img, (start_x, start_y), (width + border, start_y), (0, 0, 0), self.padding, 1)
            start_y += self.cell_size + self.padding

        # Getting coords for each cell
        start_x = int(border + self.padding + self.cell_size / 2)
        start_y = start_x

        for i in range(9):
            for j in range(3):
                self.cell_coords.append([start_x, start_y])
                start_x += self.padding + self.cell_size

            start_x = int(border + self.padding + self.cell_size / 2)
            start_y += self.padding + self.cell_size

        # cv2.circle(img, (start_x, start_y), int(cell_size / 2 * .8), (0, 0, 0), 1)

        # Insert text
        text = "Side of pool"
        font = cv2.FONT_HERSHEY_SIMPLEX

        text_size = cv2.getTextSize(text, font, 2, 2)[0]
        text_x = int((img.shape[1] - text_size[0]) / 2)
        text_y = int(border + height + border / 1.5)

        cv2.putText(img, text, (text_x, text_y), font, 2, (0, 0, 0))

        # Inserting objects onto the final grid
        coral_squares = []  # Necessary because coral is in 2 squares

        for s in all_grid_squares:
            if s.classification is not None:
                if s.classification != Object.CORAL:
                    self.insert_shapes(img, s.classification, [s.grid_num])

                else:
                    # Wait until both coral squares are found before calling insert_shapes
                    coral_squares.append(s.grid_num)

                    if len(coral_squares) == 2:
                        self.insert_shapes(img, s.classification, coral_squares)

        show_debug(img, name="frame", wait=True)

    def insert_shapes(self, img, classification, grid_num):
        """Inserts shapes onto the final grid image"""

        thickness = 5  # Line thickness

        # Circle
        if classification != Object.CORAL:
            x, y = self.cell_coords[grid_num[0] - 1]

            # Drawing the square on the grid
            if classification == Object.STAR:
                # Blue circle
                cv2.circle(img, (x, y), int(self.cell_size / 2 * .8), (255, 0, 0), thickness)

            elif classification == Object.SPONGE:
                # Green circle
                cv2.circle(img, (x, y), int(self.cell_size / 2 * .8), (0, 255, 0), thickness)

            elif classification == Object.FRAGMENT:
                # Yellow circle
                cv2.circle(img, (x, y), int(self.cell_size / 2 * .8), (0, 255, 255), thickness)

        # Ellipse
        else:
            # Check if both squares have been found before drawing
            x, y = self.cell_coords[grid_num[0] - 1]
            x2, y2 = self.cell_coords[grid_num[1] - 1]

            # Getting center coords
            x3 = int((x + x2 + self.padding) / 2)
            y3 = int((y + y2 + self.padding) / 2)

            # Setting the angle of the ellipse w/ respect to the x axis
            if x == x2:
                angle = 90
            elif y == y2:
                angle = 0

            # Red ellipse
            cv2.ellipse(img, (x3, y3), (int(self.cell_size / 1.1), int(self.cell_size / 2.8)), angle, 0, 360, (0, 0, 255),
                        thickness)

# For tracking squares on the frame
class Square:
    def __init__(self, x, y, w, h):
        self.id = 0  # Unique ID for each square
        self.x = x  # x value
        self.y = y  # y value
        self.w = w  # width
        self.h = h  # height
        self.visible = True  # True if square is visible in video
        self.delete = 0  # Tracks num of frames where visible = False
        self.screenshot_num = 0  # Tracks num of screenshots taken per square

        # Neighboring squares
        self.up = None
        self.down = None
        self.left = None
        self.right = None

# For storing screenshots of each square
class Screenshot:
    def __init__(self, id, image):
        self.id = id
        self.image = image
