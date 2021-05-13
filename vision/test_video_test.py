import cv2
from vision.test_video import undistort_bottom_video

if __name__ == '__main__':
    cam = undistort_bottom_video("transect", "3", "2.mp4")
    while True:
        img = cam.read()
        
        if img is not None:
            cv2.imshow("Vieo", img)
            cv2.waitKey(1)