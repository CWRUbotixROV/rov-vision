import numpy as np
import cv2

def point_conds(z, x1, x2, x3, x4, d1, d2, s):
    y = np.zeros(6)
    y[0] = np.sqrt((x1[0]-x2[0])**2+(x1[1]-x2[1])**2)
    y[1] = np.sqrt((x3[0]-x4[0])**2+(x3[1]-x4[1])**2)
    y[2] = 

