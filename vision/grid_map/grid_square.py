import enum

class Grid_Square:
    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y
        self.classification = None

class Object(enum.Enum):
    CORAL = 0
    FRAGMENT = 1
    SPONGE = 2
    STAR = 3