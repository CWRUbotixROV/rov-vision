import cv2
from video import Video

cap = Video(port=4777)

while True:
    while not cap.frame_available():
        continue
    img = cap.frame()
    
    cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()