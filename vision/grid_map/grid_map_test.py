import cv2
from vision.grid_map import grid_map

video = cv2.VideoCapture("../vision/grid_map/transect.MOV")

# grid_map.clear_frames()
grid_map.play_video(video)

