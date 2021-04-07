"""Contains methods to map video with lines from a mask"""

from vision.images import *
from vision.grid_map.grid_square import *
import cv2
import numpy as np


# Runs grid mapping methods
class GridMapper:
    def __init__(self):
        self.id = 0  # Unique ID for each square
        self.squares = []  # Tracks square objects
        self.images = []

    def update_frame(self, frame):
        return

    def get_contours(self, mask, frame):
        curr_squares = []  # Squares in the current frame
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, .01 * cv2.arcLength(cnt, True), True)

            if area > 10000:
                # cv2.drawContours(frame, [approx], 0, (255, 0, 0), 5)

                # Check if the contour has 4 sides
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = float(w) / h

                    # Check if sides are equal-ish lengths
                    if .5 <= aspect_ratio <= 1.5:
                        curr_squares.append(Square(-1, x, y, w, h))

        return curr_squares

    def find_squares(self, curr_squares, frame, grid_mapper):
        squares = grid_mapper.squares  # Square objects already being tracked
        matched = []  # id of squares in curr_squares matched to a square in squares

        # Check if a square should be tracked or deleted
        if len(squares) == 0:
            for s in curr_squares:
                self.id += 1
                s.id = grid_mapper.id
                squares.append(s)
                matched.append(s)

        else:
            for s in squares:
                s.visible = False

            for s1 in curr_squares:
                for s2 in squares:
                    # If a detected square is similar to a square already being tracked, update the square's info
                    if np.allclose([s1.x, s1.y, s1.w, s1.h], [s2.x, s2.y, s2.w, s2.h], atol=50):
                        s2.x = s1.x
                        s2.y = s1.y
                        s2.w = s1.w
                        s2.h = s1.h

                        s1.id = s2.id
                        matched.append(s1.id)

                        s2.visible = True
                        s2.delete = 0
                        break

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
                    s.id = grid_mapper.id
                    matched.append(s.id)
                    squares.append(s)

        self.screenshot_squares(squares, frame)

        # Drawing squares on the frame
        if config.debug:
            for s in squares:
                if s.visible:
                    cv2.putText(frame, str(s.id), (s.x + int(s.w / 2), s.y + int(s.w / 2)),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
                    cv2.rectangle(frame, (s.x, s.y), (s.x + s.w, s.y + s.h), (0, 255, 0), 5)

    def screenshot_squares(self, squares, frame):
        for s in squares:
            if s.screenshot_num != 5:
                s.screenshot_num += 1

                roi = frame[s.y:s.y + s.h, s.x:s.x + s.w]
                self.images.append(Screenshot(s.id, roi))

    def create_grid_squares(self):
        all_grid_squares = []  # Contains all Grid_Square objects

        # Creating 27 Grid_Squares
        for i in range(27):
            all_grid_squares.append(Grid_Square(i + 1))

        # Adding screenshots to the Grid_Squares
        for i in range(len(self.images)):
            screenshot = self.images[i]
            all_grid_squares[screenshot.id - 1].images.append(screenshot.image)

        return all_grid_squares

    def display_grid(self, all_grid_squares):
        cell_size = 150  # Size of each cell
        padding = 8  # Line thickness
        border = 100  # Border around grid

        width = 3 * cell_size + 4 * padding  # width of window
        height = 9 * cell_size + 10 * padding  # height of window

        img = np.zeros((height + 2 * border, width + 2 * border, 3), dtype=np.uint8)
        img.fill(255)

        # Draw vertical grid lines
        start_x = border + padding
        start_y = start_x

        for i in range(4):
            cv2.line(img, (start_x, start_y), (start_x, height + border), (0, 0, 0), padding, 1)
            start_x += cell_size + padding

        # Draw horizontal grid lines
        start_x = border + padding  # Reset x position

        for i in range(10):
            cv2.line(img, (start_x, start_y), (width + border, start_y), (0, 0, 0), padding, 1)
            start_y += cell_size + padding

        # Getting coords for each cell
        cell_coords = []

        start_x = int(border + padding + cell_size / 2)
        start_y = start_x

        for i in range(9):
            for j in range(3):
                cell_coords.append([start_x, start_y])
                start_x += padding + cell_size

            start_x = int(border + padding + cell_size / 2)
            start_y += padding + cell_size

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
                    self.insert_shapes(img, s.classification, [s.grid_num], cell_coords, cell_size, padding)

                else:
                    # Wait until both coral squares are found before calling insert_shapes
                    coral_squares.append(s.grid_num)

                    if len(coral_squares) == 2:
                        self.insert_shapes(img, s.classification, coral_squares, cell_coords, cell_size, padding)

        show_debug(img, name="frame", wait=True)

    # Inserts shapes on the grid display
    def insert_shapes(self, img, classification, grid_num, cell_coords, cell_size, padding):
        thickness = 5  # Line thickness

        # Circle
        if classification != Object.CORAL:
            x, y = cell_coords[grid_num[0] - 1]

            # Drawing the square on the grid
            if classification == Object.STAR:
                cv2.circle(img, (x, y), int(cell_size / 2 * .8), (255, 0, 0), thickness)  # Blue circle

            elif classification == Object.SPONGE:
                cv2.circle(img, (x, y), int(cell_size / 2 * .8), (0, 255, 0), thickness)  # Green circle

            elif classification == Object.FRAGMENT:
                cv2.circle(img, (x, y), int(cell_size / 2 * .8), (0, 255, 255), thickness)  # Yellow circle

        # Ellipse
        else:
            # Check if both squares have been found before drawing
            x, y = cell_coords[grid_num[0] - 1]
            x2, y2 = cell_coords[grid_num[1] - 1]

            # Getting center coords
            x3 = int((x + x2 + padding) / 2)
            y3 = int((y + y2 + padding) / 2)

            # Setting the angle of the ellipse w/ respect to the x axis
            if x == x2:
                angle = 90
            elif y == y2:
                angle = 0

            # Drawing the ellipse
            cv2.ellipse(img, (x3, y3), (int(cell_size / 1.1), int(cell_size / 2.8)), angle, 0, 360, (0, 0, 255),
                        thickness)  # Red ellipse


# For tracking squares on the frame
class Square:
    def __init__(self, id, x, y, w, h):
        self.id = id  # Unique ID for each square
        self.x = x  # x value
        self.y = y  # y value
        self.w = w  # width
        self.h = h  # height
        self.visible = True  # True if square is visible in video
        self.delete = 0  # Tracks num of frames where visible = False
        self.screenshot_num = 0  # Tracks num of screenshots taken per square


# For storing screenshots of each square
class Screenshot:
    def __init__(self, id, image):
        self.id = id
        self.image = image
