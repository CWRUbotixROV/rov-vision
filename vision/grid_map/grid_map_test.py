import cv2
from vision.grid_map import grid_map
from vision.images import *

video = get_video("transect", "transect.MOV")

# Tests color and line detection
grid_map.start_mapping(video)

# Tests image stitching
# grid_map.image_stitching()

