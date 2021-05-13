import numpy as np
import cv2

#DIM=(640, 480)
# K=np.array([[248.03350661168776, 0.0, 330.5324270301757], [0.0, 249.47801268319506, 250.434877474223], [0.0, 0.0, 1.0]])
# D=np.array([[0.001076093769471156], [-0.029445141629456474], [0.011446340748514342], [-0.002986122649406739]])

#K=np.array([[377.3888646039447, 0.0, 327.4794856163454], [0.0, 376.9743701067552, 218.40744705923333], [0.0, 0.0, 1.0]])
#D=np.array([[-0.04766298130789896], [-0.026480276293633788], [0.09205241438909044], [-0.08608273587396821]])
def undistort(img):
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img

def undistort(img, DIM, K, D, balance=0.0, dim2=None, dim3=None):
    dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    if not dim2:
        dim2 = dim1
    if not dim3:
        dim3 = dim1
    scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0    # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img
    
if __name__ == '__main__':
    cam = cv2.VideoCapture("C:\\Users\\rykar\\Pictures\\Camera Roll\\WIN_20210427_20_27_29_Pro.mp4")
    while True:
        ret, img = cam.read()
        cv2.imshow("Undistort", img)
        cv2.waitKey(0)
        if img is not None:
            img = img[0:1080, 240:1680]
            cv2.imshow("Image", undistort(img, balance=0.25))
            cv2.waitKey(1)