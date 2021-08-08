import enum

class Grid_Square:
    def __init__(self, id):
        self.id = id  # For matching screenshots to the right Grid_Square
        self.grid_num = 0  # Square number for final grid map
        self.images = []  # Screenshots
        self.classification = None  # Based on object detection

class Object(enum.Enum):
    CORAL = 0
    FRAGMENT = 1
    SPONGE = 2
    STAR = 3