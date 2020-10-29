import cv2 as cv2
import numpy as np

class Video_Stream_Test:

    select = []
    index_of_select = 0
    videos = []
    frame = null
    file_paths = []

    def __init__(self, file_paths):
        self.file_paths = file_paths
        for path in file_paths:
            videos.append(cv2.VideoCapture(file_paths))
        select = [index_of_select]

    def next(self):
        if (len(select) > index_of_select):
            index_of_select = index_of_select + 1
        else:
            index_of_select = 0

    def frames(self):
        for i in range(0, 5, 1):
            self.frame = cv2.VideoCapture(index_of_select)


#while(True):
    # Capture frame-by-frame
    #ret, frame = cap.read()

    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    #cv2.imshow('frame',gray)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
        #break

# When everything done, release the capture
#cap.release()
#cv2.destroyAllWindows()