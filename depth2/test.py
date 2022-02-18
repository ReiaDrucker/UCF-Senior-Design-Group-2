#!/bin/env python3
# TODO: pytest

import depth_algo as depth
import matplotlib.pyplot as plt

import cv2 as cv
import numpy as np
import math

# r_path = '../data/tsukuba/NewTsukubaStereoDataset/illumination/daylight/left/tsukuba_daylight_L_00005.png'
# l_path = '../data/tsukuba/NewTsukubaStereoDataset/illumination/daylight/right/tsukuba_daylight_R_00005.png'

l_path = '../data/left.tif'
r_path = '../data/right.tif'

# l_path = '../../data/left.png'
# r_path = '../../data/right.png'

# l_path = '/home/shado/workspace/edu/cop4934/kitti_sample/2011_09_26/2011_09_26_drive_0020_extract/image_01/data/0000000000.png'
# r_path = '/home/shado/workspace/edu/cop4934/kitti_sample/2011_09_26/2011_09_26_drive_0020_extract/image_02/data/0000000000.png'


left = cv.imread(l_path, cv.IMREAD_GRAYSCALE)
right = cv.imread(r_path, cv.IMREAD_GRAYSCALE)

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

    left = stereo.left if len(stereo.left.shape) == 3 else cv.cvtColor(stereo.left, cv.COLOR_GRAY2RGB)
    right = stereo.right if len(stereo.left.shape) == 3 else cv.cvtColor(stereo.right, cv.COLOR_GRAY2RGB)

    shape = (
        min(left.shape[0], right.shape[0]),
        min(left.shape[1], right.shape[1])
    )

    frame = left[:shape[0], :shape[1]] * z
    frame = frame + right[:shape[0], :shape[1]] * (1 - z)
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

# pose.refine()
# print(pose)

stereo.rectify(pose)

left = stereo.get_image(0)
right = stereo.get_image(1)
matches = pose.get_matches()
frame = debug_frame(StereoPair(left, right, matches), 0.5, True)

n = matches.shape[0]
print(matches.shape)
dx = np.array([matches[i,1,0] - matches[i,0,0] for i in range(n)])
print('dx:', dx.mean(), dx.max(), dx.min())

plt.imshow(frame)
plt.show()

min_disp = int(dx.min())
max_disp = dx.max()
num_disp = (int(max_disp - min_disp + 15) // 16) * 16

print(min_disp, num_disp)

# TODO: do a better job detecting min/num disparities
# especially in cases where the disparity might be reversed
# -2, 10 for target image
cloud = depth.PointCloud(stereo, -2, 10, 3, 1.5)
disp = cloud.get_disparity()
print(disp.min(), disp.max())
plt.imshow(disp, cmap='gray')
plt.show()

np.save('disp', disp)
cv.imwrite('rgb.png', right)
