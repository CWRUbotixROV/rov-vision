import cv2
from vision.grid_map import grid_map

cap = cv2.VideoCapture("../vision/grid_map/transect.MOV")

grid_map.test(cap)

