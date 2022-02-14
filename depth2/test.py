#!/bin/env python3
# TODO: pytest

import depth_algo as depth
import matplotlib.pyplot as plt

import cv2 as cv
import numpy as np
import math

left = cv.imread('../data/left.tif', cv.IMREAD_GRAYSCALE)
right = cv.imread('../data/right.tif', cv.IMREAD_GRAYSCALE)

stereo = depth.ImagePair(left, right)
stereo.fill_matches()

left = stereo.get_image(0)
plt.imshow(left)
plt.show()

pose = depth.CameraPose(stereo, 75 * math.pi / 180)
pose.refine()
