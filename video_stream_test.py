"""
Displays a UDP video stream on a given port.
"""

import cv2
from video import Video
import sys


cap = Video(port=sys.argv[1])
img_count = 0

while True:
    while not cap.frame_available():
        continue
    img = cap.frame()
    
    cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1)==ord('p'):
        cv2.imwrite(f"image_{img_count}.png", img)
        img_count += 1

cv2.destroyAllWindows()