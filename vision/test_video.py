import numpy as np

from vision.images import get_video
from vision.lens_correction import undistort

class UndistortedCam:
    def __init__(self, cam, dim, k, d):
        self.cam = cam
        self.dim = dim
        self.k = k
        self.d = d
    
    def read(self):
        ret, img = self.cam.read()
        if img is not None:
            return undistort(img, self.dim, self.k, self.d, balance=0.25)

"""Takes in a file path and returns an object that returns the frames of the video undistorted every time read() is called.
This is calibrated for the bottom camera used on the transect line. See test_video_test.py as an example"""
def undistort_bottom_video(*paths):
    DIM=(1920, 1080)
    K=np.array([[855.9762510114691, 0.0, 961.2347612376141], [0.0, 855.0332533773513, 505.3971595249296], [0.0, 0.0, 1.0]])
    D=np.array([[-0.08245436545678554], [0.1378375094314711], [-0.20612424952871777], [0.10526202213131022]])
    
    cam = get_video(*paths)

    return UndistortedCam(cam, DIM, K, D)