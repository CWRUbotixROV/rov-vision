import cv2
import os
from vision.grid_map import grid_map

video = cv2.VideoCapture("../vision/grid_map/transect.MOV")

grid_map.image_stitching()
# grid_map.play_video(video)

