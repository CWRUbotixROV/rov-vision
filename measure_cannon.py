import numpy as np
import cv2
import scipy.linalg as la
import scipy.optimize as opt

SCALE = 1e-3/1.12e-6    # mm/pixel

def points_cond(y, m1, m2, A, d):
    """
    Function for opt.root.

    Arguments:
        y : [x1, x2, y1, y2, z]
        m1 : the first image point [u1, v1]
        m2 : the second image point [u2, v2]
        A : the camera matrix
        d : the distance between the points
    """
    yp = np.zeros(3)
    x1, x2, y1, y2, z = y
    f = A[0,0]
    cx = A[0,2]
    cy = A[1,2]
    yp[0] = x1-z*SCALE*(f*m1[0]+cx)
    yp[1] = x2-z*SCALE*(f*m2[0]+cx)
    yp[2] = y1-z*SCALE*(f*m1[1]+cy)
    yp[3] = y2-z*SCALE*(f*m2[1]+cy)
    yp[4] = (x1-x2)**2+(y1-y2)**2-d**2
    return yp

def measure(m1, m2, m3, m4, d1, d2, image):
    h, w, _ = image.shape
    # Camera matrix
    A = np.array([
        [3.04, 0, w/2*SCALE],
        [0, 3.04, h/2*SCALE],
        [0, 0, 1]
    ])
    # cv2.undistort()
    s1 = opt.root(points_cond, x0=np.array([0, 0, d1, 0, 1]), args=(m1, m2, A, d1))
    s2 = opt.root(points_cond, x0=np.array([0, 0, d2, 0, 1]), args=(m3, m4, A, d2))
    p1 = np.array([s1[0], s1[2], s1[4]])
    p2 = np.array([s1[1], s1[3], s1[4]])
    p3 = np.array([s2[0], s2[2], s2[4]])
    p4 = np.array([s2[1], s2[3], s2[4]])
    mp1 = (p1+p2)/2
    mp2 = (p3+p4)/2
    length = la.norm(mp1, mp2)
    longer = max(la.norm(p1, p2), la.norm(p3, p4))
    shorter = min(la.norm(p1, p2), la.norm(p3, p4))
    print(f"Length: {length}")
    print(f"Longer diameter: {longer}")
    print(f"Shorter diameter {shorter}")
    return length, longer, shorter

