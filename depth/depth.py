import cv2 as cv
import numpy as np

if __package__:
    from . import util
else:
    import util

EPS = 1e-15

def uvd_to_xyz(uvd, f, b):
    u = uvd[:,:,0]
    v = uvd[:,:,1]
    d = uvd[:,:,2]

    z = f * b / (d + EPS)
    z[z < 0] = 0

    x = u * z / f
    y = v * z / f

    return x, y, z


def make_xyz(disparity, f, b):
    h, w = disparity.shape
    cx, cy = w / 2, h / 2

    u = np.arange(-cx, w - cx, 1)
    v = np.arange(-cy, h - cy, 1)
    u, v = np.meshgrid(u, v)

    uvd = np.stack((u, v, disparity), -1)

    x, y, z = uvd_to_xyz(uvd, f, b)
    return np.stack((x, y, z), -1)

def get_xyz(depth, u, v):
    # TODO: this lerp doesn't necessarily map to a point in the same direction
    # should probably fix that.
    h, w = depth.shape[:2]

    u0 = int(u)
    u1 = u0 + 1
    v0 = int(v)
    v1 = v0 + 1

    def bound(a, b, c):
        if a < b:
            return b
        if a > c:
            return c;
        return a
    u0 = bound(u0, 0, w-1)
    u1 = bound(u1, 0, w-1)
    v0 = bound(v0, 0, h-1)
    v1 = bound(v1, 0, h-1)

    a0 = util.lerp(depth[v0, u0], depth[v0, u1], u0, u1, u)
    a1 = util.lerp(depth[v1, u0], depth[v1, u1], u0, u1, u)
    return util.lerp(a0, a1, v0, v1, v)

if __name__ == '__main__':
    from matching import ImageWithFeatures, remove_match_outliers
    from disparity import disparity_uncalibrated

    left = ImageWithFeatures(cv.imread('../data/left.tif', cv.IMREAD_GRAYSCALE), 1024, 0, -3.5)
    right = ImageWithFeatures(cv.imread('../data/right.tif', cv.IMREAD_GRAYSCALE), 1024)

    disparity = disparity_uncalibrated(left, right, verbose=True)

    # Currently just guessing these, based on vizualization in cloud.py
    baseline = .55 # in meters (?)
    focal_length = 1000 / baseline # ~1818, in pixels

    xyz = make_xyz(disparity, focal_length, baseline)

    print(xyz.shape)
