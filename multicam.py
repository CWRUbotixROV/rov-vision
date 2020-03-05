import cv2
import numpy as np
from video import Video
import time


# cap = Video(port=sys.argv[1])
cap = Video(port=4777, appsink=0)   # primary camera
cap2 = Video(port=4780, appsink=1)  # secondary camera

while True:
    while not cap.frame_available():
        continue
    img = cap.frame()
    if cap2.frame_available():
        img2 = cap2.frame()
    else:
        img2 = np.zeros_like(img)
    
    # we use numpy's vstack method to efficiently combine the frames into rows and columns on the display
    # to add more cameras, vstack the next column and then use hstack to combine the columns
    combined = np.vstack((img, img2))
    cv2.imshow('img', combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    time.sleep(0.01)    # this is needed to keep all of my laptop's CPU from getting used up for unclear reasons

cv2.destroyAllWindows()