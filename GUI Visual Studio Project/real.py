# FIXME: I'm too lazy to figure out how Visual Studio manages the pythonpath right now
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from depth import matching, disparity, depth

import numpy as np
import cv2 as cv

def qToCv(q):
    w = q.width()
    h = q.height()
    b = q.constBits()
    b.setsize(h * w * 3)
    img = np.array(b).reshape((h, w, 3))
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

def getRealFromImages(left, right):
    left = matching.ImageWithFeatures(qToCv(left), 1024)
    right = matching.ImageWithFeatures(qToCv(right), 1024)
    matches = np.array(left.match(right))

    rectified = disparity.rectify(left.img, right.img, matches)
    disparity_w = disparity.disparity(rectified.left, rectified.right, rectified.matches)
    disp = disparity.unrectify(disparity_w, rectified.h1, left.img.shape)

    # TODO: wire the focal length estimator here instead of guessing
    baseline = .55
    focal_length = 1000 / baseline

    xyz = depth.make_xyz(disp, focal_length, baseline)
    return xyz

