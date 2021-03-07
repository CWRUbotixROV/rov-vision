from vision.line_detection.line_detection import *
from vision.colors import *
from vision.images import *

config.debug = True

video = get_video("rov-vision\images\transect\1", "1.mp4")

draw_lines()