import cv2 as cv2
import numpy as np

class Video_Stream_Capture:

    index_of_select = 0
    videos = []
    frame = None
    file_paths = []

    def __init__(self, file_paths, select):
        self.file_paths = file_paths
        for path in file_paths:
            videos.append(cv2.VideoCapture(file_paths))
        self.select = select

    def next(self):
        if ((len(videos) - 1) > index_of_select):
            index_of_select = index_of_select + 1
        else:
            index_of_select = 0

    def frames(self):
        i=0
        captures = []
        for video in videos:
            ret, frame = video.read()
            if ret == False:
                break
            captures.append(cv.2.imwrite('frame' + str(i) + '.jpg', frame))
            i+=1
        videos.release()
        return captures