from matching import ImageWithFeatures, remove_match_outliers
from disparity import disparity_uncalibrated

import numpy as np
import cv2 as cv

EPS = 1e-15

def uvd_to_xyz(uvd, f, b):
    u = uvd[:,:,0]
    v = uvd[:,:,1]
    d = uvd[:,:,2]

    z = f * b / (d + EPS)
    x = u * z / f
    y = v * z / f

    return x, y, z


def make_rgbxyz(rgb, disparity, f, b):
    h, w = rgb.shape[:2]
    cx, cy = w / 2, h / 2

    u = np.arange(-cx, w - cx, 1)
    v = np.arange(-cy, h - cy, 1)
    u,v = np.meshgrid(u, v)
    uvd = np.stack((u, v, disparity), -1)

    x, y, z = uvd_to_xyz(uvd, f, b)
    return np.stack((*cv.split(rgb), x, y, z), -1)


if __name__ == '__main__':
    left = ImageWithFeatures(cv.imread('../data/left.tif', cv.IMREAD_GRAYSCALE), 1024, 0, -3.5)
    right = ImageWithFeatures(cv.imread('../data/right.tif', cv.IMREAD_GRAYSCALE), 1024)

    disparity = disparity_uncalibrated(left, right, verbose=True)

    # Currently just guessing these, based on vizualization in cloud.py
    baseline = .55 # in meters (?)
    focal_length = 1000 / baseline # ~1818, in pixels

    rgbxyz = make_rgbxyz(left.img, disparity, focal_length, baseline)

    print(rgbxyz.shape)
