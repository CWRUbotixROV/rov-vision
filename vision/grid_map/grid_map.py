"""Contains methods to map video with lines from a mask"""

from vision.images import *
import cv2
import numpy as np


def draw_lines(frame, mask):
    """Draws HoughLines on image
    For example: 'draw_lines(frame, edges)'"""
    lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=100)

    if lines is not None:
        for i in range(len(lines)):
            line = lines[i]

            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


class GridMapper:
    def __init__(self, id, squares=[], images=[]):
        self.id = id  # Unique ID for each square
        self.squares = squares  # Tracks square objects
        self.images = images

    def update_id(self):
        self.id += 1

class Square:
    def __init__(self, id, x, y, w, h):
        self.id = id  # Unique ID for each square
        self.x = x  # x value
        self.y = y  # y value
        self.w = w  # width
        self.h = h  # height
        self.visible = True  # True if square is visible in video
        self.delete = 0  # Tracks num of frames visible = False
        self.screenshot_num = 0  # Tracks num of screenshots taken per square


def get_contours(mask, frame):
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


def find_squares(curr_squares, frame, grid_mapper):
    squares = grid_mapper.squares  # Square objects already being tracked
    matched = []  # id of squares in curr_squares matched to a square in squares

    # Check if a square should be tracked or deleted
    if len(squares) == 0:
        for s in curr_squares:
            grid_mapper.update_id()
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
                grid_mapper.update_id()
                s.id = grid_mapper.id
                matched.append(s.id)
                squares.append(s)

    screenshot_squares(squares, frame, grid_mapper)

    # Drawing squares on the frame
    if config.debug:
        for s in squares:
            if s.visible:
                cv2.putText(frame, str(s.id), (s.x + int(s.w / 2), s.y + int(s.w / 2)),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
                cv2.rectangle(frame, (s.x, s.y), (s.x + s.w, s.y + s.h), (0, 255, 0), 5)

class SquareImage:
    def __init__(self, name, image):
        self.name = name
        self.image = image


def screenshot_squares(squares, frame, grid_mapper):
    for s in squares:
        if s.screenshot_num != 5:
            s.screenshot_num += 1

            roi = frame[s.y:s.y + s.h, s.x:s.x + s.w]
            image_name = str(s.id) + "(" + str(s.screenshot_num) + ")"
            grid_mapper.images.append(SquareImage(image_name, roi))

            # file_name = str(s.id) + "(" + str(s.screenshot_num) + ").jpg"
            # cv2.imwrite(get_folder("transect", "squares") + "/" + file_name, roi)

# Class for the shapes that need to be mapped
class Shape:
    def __init__(self, name, square_id):
        self.name = name
        self.square_id = square_id  # What square(s) it is located in


def display_grid():
    cell_size = 150
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
    show_debug(img, name="frame", wait=True)


# Inserts shapes on the grid display
def insert_shapes(shape, img, cell_coords, cell_size):
    if len(shape.square_id) == 1:
        x, y = cell_coords[shape.square_id[0]]
    elif len(shape.square_id) == 2:
        x, y = cell_coords[shape.square_id[0]]
        x2, y2 = cell_coords[shape.square_id[1]]

    if shape.name == "sea star":
        cv2.circle(img, (x, y), int(cell_size / 2 * .8), (0, 0, 0), 1)

    elif shape.name == "sponge":
        cv2.circle(img, (x, y), int(cell_size / 2 * .8), (0, 0, 0), 1)

    elif shape.name == "coral fragment":
        cv2.circle(img, (0, 0), int(cell_size / 2 * .8), (0, 0, 0), 1)
    else:
        print("ERROR")
