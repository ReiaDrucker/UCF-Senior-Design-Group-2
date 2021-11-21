import numpy as np
import cv2 as cv

def warp_points(x, h):
    n = len(x)
    x = np.vstack((x.transpose(), np.ones(n)))
    x = np.matmul(h, x).transpose()
    return cv.convertPointsFromHomogeneous(x)[:,0]

def correct_homographies(H, S, L):
    pts = []

    for h, s in zip(H, S):
        x = np.array([
            [0, 0],
            [0, s[0]],
            [s[1], 0],
            [s[1], s[0]]
        ])

        x = warp_points(x, h)
        pts += list(x)

    pts = np.array(pts)

    x0 = np.min(pts[:,0])
    x1 = np.max(pts[:,0])
    y0 = np.min(pts[:,1])
    y1 = np.max(pts[:,1])

    w = x1 - x0
    h = y1 - y0

    scale = max(w / L[0], h / L[1])

    correction = np.array([
        [1, 0, -x0],
        [0, 1, -y0],
        [0, 0, scale]
    ])

    return [np.matmul(correction, h) for h in H]
        
