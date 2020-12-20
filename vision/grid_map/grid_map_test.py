import cv2
from vision.grid_map import grid_map
from vision.images import *

video = get_video("transect", "transect.MOV")

# Tests image stitching
# grid_map.image_stitching()

# Tests color and line detection
# grid_map.play_video(video)

# Redoing color detection with k means clustering
grid_map.test(video, 1)

