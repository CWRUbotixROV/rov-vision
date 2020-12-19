import cv2
from vision.grid_map import grid_map
from vision.images import *

video = get_video("transect", "transect.MOV")

# grid_map.image_stitching()
grid_map.play_video(video)

