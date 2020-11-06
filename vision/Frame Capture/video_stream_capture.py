import cv2 as cv2
import numpy as np

class Video_Stream_Capture:

    select = []
    index_of_select = 0
    videos = []
    frame = null
    file_paths = []

    def __init__(self, file_paths, select):
        self.file_paths = file_paths
        for path in file_paths:
            videos.append(cv2.VideoCapture(file_paths))
        self.select = select

    def next(self):
        if (len(select) > index_of_select):
            index_of_select = index_of_select + 1
        else:
            index_of_select = 0

    def frames(self):
        #for i in range(0, 5, 1):
            self.frame = cv2.VideoCapture(index_of_select)