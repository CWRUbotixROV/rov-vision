from vision.colors import *
from vision.images import get_image
from vision import config

config.debug = True

image = get_image("coral", "1", "1.jpg")

print(get_colors(image, 10))
