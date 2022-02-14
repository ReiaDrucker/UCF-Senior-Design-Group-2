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

from collections import namedtuple
StereoPair = namedtuple('StereoPair', 'left, right, matches')
def _lerp(a, b, x):
    return np.add(np.multiply(a, x), np.multiply(b, 1 - x))
def _sigmoid(x):
    return 1 / (1 + math.exp(-x))
def debug_frame(stereo, z, lines = False):
    '''
    For debugging.
    Generate a frame interopolating between the left and right images.
    '''
    norm_dx = np.max(abs(stereo.matches[:,0,0] - stereo.matches[:,1,0]))

    shape = (
        min(stereo.left.shape[0], stereo.right.shape[0]),
        min(stereo.left.shape[1], stereo.right.shape[1])
    )

    frame = stereo.left[:shape[0], :shape[1]] * z
    frame = frame + stereo.right[:shape[0], :shape[1]] * (1 - z)
    frame[frame > 255] = 255
    frame = frame.astype('uint8')

    for i in range(stereo.matches.shape[0]):
        u = stereo.matches[i,0]
        v = stereo.matches[i,1]

        color = (0, 255, 0)
        color = _lerp((255, 0, 0), (0, 0, 255), _sigmoid((u[0] - v[0]) / norm_dx))

        if lines:
            cv.line(frame, u.astype(int), v.astype(int), color, 2)
        else:
            cv.circle(frame, _lerp(u, v, z).astype(int), 1, color, -1)

    return frame

pose = depth.CameraPose(stereo, 75 * math.pi / 180)
print(pose)

pose.refine()
print(pose)

stereo.rectify(pose)

left = stereo.get_image(0)
right = stereo.get_image(1)
matches = pose.get_matches()
frame = debug_frame(StereoPair(left, right, matches), .5, True)
plt.imshow(frame)
plt.show()
