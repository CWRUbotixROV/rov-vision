import enum
import itertools
import cv2
from vision.colors import get_colors


class ImageColors:
    def __init__(self, image):
        self.image = image
        self.colors = edge_colors(image)

    def rotate(self):
        return ImageColors(cv2.rotate(self.image, cv2.ROTATE_180))

class Face(enum.Enum):
    back = 0
    front = 1
    left = 2
    right = 3
    top = 4
    
class Edge(enum.Enum):
    left = 0
    top = 1
    right = 2
    bottom = 3

def match(squares, rects):
    squares = [ImageColors(square) for square in squares]
    rects = [ImageColors(rect) for rect in rects]

    min_score = None
    min_arrangement = None
    # Choose the arrangement with the lowest score
    for arrangement in make_arrangements(squares, rects):
        score = evaluate_arrangement(arrangement)
        if (min_score is None or score < min_score):
            min_score = score
            min_arrangement = arrangement


    return min_arrangement

def make_arrangements(squares, rects):
    arrangements = []
    perms = list(itertools.permutations(rects))

    for perm in perms:
        arrangement1 = {
            Face.left : squares[0],
            Face.right : squares[1],
            Face.front : perm[0],
            Face.back : perm[1],
            Face.top : perm[2]
        }
        arrangements.append(arrangement1)

        arrangement2 = {
            Face.left : squares[0],
            Face.right : squares[1],
            Face.front : perm[0],
            Face.back : perm[1],
            Face.top : perm[2].rotate()
        }
        arrangements.append(arrangement2)

    return arrangements

left_right_pairs = (
    (Face.front, Face.right),
    (Face.right, Face.back),
    (Face.back, Face.left),
    (Face.left, Face.front)
)

face_edge_pairs = {
    Face.front : Edge.bottom,
    Face.left : Edge.left,
    Face.right : Edge.right,
    Face.back : Edge.top
}

def evaluate_arrangement(arrangement):
    """Returns the score indicicating how well the edges match in an arrangement"""
    score = 0
    for (left_face, right_face) in left_right_pairs:
        color1 = arrangement[left_face].colors[Edge.right]
        color2 = arrangement[right_face].colors[Edge.left]
        score += color_dist(color1, color2)

    for (face, edge) in face_edge_pairs.items():
        color1 = arrangement[face].colors[Edge.top]
        color2 = arrangement[Face.top].colors[edge]
        score += color_dist(color1, color2)
    
    return score

def edge_colors(image):
    main_color = get_colors(image, 1)[0]
    color_dict = {}
    for edge in Edge:
        cropped = crop_edge(image, edge)
        color1, color2 = get_colors(cropped, 2)

        dist1 = color_dist(main_color, color1)
        dist2 = color_dist(main_color, color2)

        # Choose the color least like the main_color
        if dist1 > dist2:
            color = color1
        else:
            color = color2

        color_dict[edge] = color
    
    return color_dict

def crop_edge(image, edge):
    height, width, _ = image.shape
    thickness = int(height / 3)

    x1 = 0
    x2 = width - 1
    y1 = 0
    y2 = height - 1

    if edge == Edge.left:
        x2 = thickness
    elif edge == Edge.right:
        x1 = width - thickness
    elif edge == Edge.top:
        y2 = thickness
    else:
        y1 = height - thickness

    return image[y1:y2, x1:x2]

def color_dist(color1, color2):
    """Returns the sum of the difference sqared of each color channel"""
    total = 0
    for i in range(len(color1)):
        total += (color1[i] - color2[i]) ** 2
    return total