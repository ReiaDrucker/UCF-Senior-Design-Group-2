'''
Tools for getting disparity from a stereo pair and matches.

Typically:
1. rectified = rectify(left, right, matches)
2. disp = disparity(rectified...)
3. unrectify(disp)
'''

import cv2 as cv
import numpy as np
import random
import math
from collections import namedtuple

from matplotlib import pyplot as plt

def _h2e(X):
    return (X / X[-1])[:-1]

def _rectify_shearing(H1, shape):
    '''
    Adjust shearing homography to preserve aspect ratio using remaining degrees of freedom
    https://scicomp.stackexchange.com/a/2908
    '''
    h, w = shape[:2]

    a = np.float32([ (w-1)/2.0,    0,            1 ])
    b = np.float32([ (w-1),        (h-1)/2.0,    1 ])
    c = np.float32([ (w-1)/2.0,    (h-1),        1 ])
    d = np.float32([ 0,            (h-1)/2.0,    1 ])

    # TODO: stop using _h2e
    a_prime = _h2e(np.matmul(H1, a.transpose()))
    b_prime = _h2e(np.matmul(H1, b.transpose()))
    c_prime = _h2e(np.matmul(H1, c.transpose()))
    d_prime = _h2e(np.matmul(H1, d.transpose()))

    x = b_prime - d_prime
    y = c_prime - a_prime

    k1 = (h*h*x[1]*x[1] + w*w*y[1]*y[1]) / (h*w*(x[1]*y[0] - x[0]*y[1]))
    k2 = (h*h*x[0]*x[1] + w*w*y[0]*y[1]) / (h*w*(x[0]*y[1] - x[1]*y[0]))

    if (k1 < 0): # Why this?
        k1 *= -1
        k2 *= -1

    return np.float32([
        [k1, k2, 0],
        [0, 1, 0],
        [0, 0, 1]])

def _correct_rectification(h1, h2, shape1, shape2):
    '''
    Rectify shearing and translate / scale to fit in an LxL box,
    where L is the largest coordinate from shape1
    '''
    L = np.max(shape1[:2])

    s1 = _rectify_shearing(h1, shape1)
    s2 = _rectify_shearing(h2, shape2)
    h1 = np.matmul(s1, h1)
    h2 = np.matmul(s2, h2)

    h, w = shape1[:2]
    x1_ = [[0, 0, 1],
           [w, 0, 1],
           [0, h, 1],
           [w, h, 1]]
    x1_ = np.transpose(x1_)

    x1_ = np.matmul(h1, x1_)
    x1_[0] /= x1_[-1]
    x1_[1] /= x1_[-1]
    lx = x1_[0].min()
    ly = x1_[1].min()
    hx = x1_[0].max()
    hy = x1_[1].max()

    T = [[1, 0, -lx],
         [0, 1, -ly],
         [0, 0, 1]]

    sx = L / (hx - lx)
    sy = L / (hy - ly)
    S = [[sx, 0, 0],
         [0, sy, 0],
         [0, 0, 1]]

    h1 = np.matmul(np.matmul(S, T), h1)
    h2 = np.matmul(np.matmul(S, T), h2)

    return h1, h2

Rectified = namedtuple('Rectified', 'left, right, matches, h1, h2')
def rectify(left, right, matches, H = None, verbose = False):
    '''
    Rectify a stereo pair and matches by estimating the fundamental matrix,
    or by using a provided pair of homographies H = (h1, h2)
    '''
    L = max(left.shape[:2])
    x1 = matches[:, 0]
    x2 = matches[:, 1]

    F, F_mask = cv.findFundamentalMat(x1, x2, method=cv.FM_LMEDS)
    F_mask = F_mask.flatten()
    x1 = x1[F_mask == 1]
    x2 = x2[F_mask == 1]

    if verbose:
        print('F:', F)
        print('Inlier points:', len(x1))

    h1, h2 = None, None
    if H is not None:
        h1, h2 = H
    else:
        ret, h1, h2 = cv.stereoRectifyUncalibrated(x1, x2, F, (left.shape[1], left.shape[0]), threshold = 0)
        if not ret:
            raise RuntimeError('Failed to generate rectification homographies')

    h1, h2 = _correct_rectification(h1, h2, left.shape, right.shape)

    left_w = cv.warpPerspective(left, h1, (L, L))
    right_w = cv.warpPerspective(right, h2, (L, L))

    n = len(x1)
    x1 = np.vstack((x1.transpose(), np.ones(n)))
    x1 = np.matmul(h1, x1).transpose()

    x2 = np.vstack((x2.transpose(), np.ones(n)))
    x2 = np.matmul(h2, x2).transpose()

    x1 = cv.convertPointsFromHomogeneous(x1)[:,0]
    x2 = cv.convertPointsFromHomogeneous(x2)[:,0]

    matches_w = np.c_[x1, x2]
    matches_w = matches_w.reshape(matches_w.shape[0], 2, 2)

    return Rectified(left_w, right_w, matches_w, h1, h2)

def _measure_disparity(matches):
    '''
    Approximate minimum and maximum disparity to set window sizes for SGBM
    '''
    dxs = [matches[i,0,0] - matches[i,1,0] for i in range(len(matches))]
    iqr = np.quantile(dxs, .75) - np.quantile(dxs, .25)
    min_disp = math.floor(max(min(dxs), np.quantile(dxs, .25) - 1.5 * iqr))
    max_disp = math.ceil(min(max(dxs), np.quantile(dxs, .75) + 1.5 * iqr))
    return min_disp, max_disp

def disparity(left, right, matches, verbose = False):
    '''
    Calculate the disparity from a pair of (rectified) images and matches
    '''
    min_disp, max_disp = _measure_disparity(matches)

    swapped = False
    if max_disp < 0 or (min_disp < 0 and max_disp < -min_disp):
        if verbose:
            print('Negative disparity, swapping images')

        swapped = True
        min_disp, max_disp = -max_disp, -min_disp
        left, right = right, left

    num_disp = max_disp - min_disp + 1
    num_disp = ((num_disp + 15) // 16) * 16 # Needs to be divisible by 16
    win_size = 0

    if verbose:
        print('min disp:', min_disp)
        print('num disp:', num_disp)
        print('win size:', win_size)

    #Create Block matching object.
    stereo = cv.StereoSGBM_create(minDisparity = min_disp,
                                  numDisparities = num_disp,
                                  blockSize = 3,
                                  uniquenessRatio = 5,
                                  speckleWindowSize = 5,
                                  speckleRange = 5,
                                  disp12MaxDiff = 0,
                                  P1 = 8*3*win_size**2,
                                  P2 = 32*3*win_size**2)

    disparity = stereo.compute(left, right)

    if verbose:
      plt.imshow(disparity)
      plt.show()

    right_stereo = cv.ximgproc.createRightMatcher(stereo)
    right_disparity = right_stereo.compute(right, left)

    if swapped:
        left, right = right, left
        disparity, right_disparity = right_disparity, disparity
        stereo, right_stereo = right_stereo, stereo

    wls_filter = cv.ximgproc.createDisparityWLSFilter(stereo)
    wls_filter.setLambda(8000)
    wls_filter.setSigmaColor(1.5)

    return wls_filter.filter(disparity, left, disparity_map_right=right_disparity)

def unrectify(disparity, h, shape):
    '''
    Apply inverse rectification homography for an image
    '''
    return cv.warpPerspective(disparity, np.linalg.inv(h), (shape[1], shape[0]))

if __name__ == '__main__':
    from matching import ImageWithFeatures

    # Still no good way to find ty besides manual tuning,
    # but it is very important to get it right to avoid distortion during rectification
    # 3.5 pixels seems OK
    left = ImageWithFeatures(cv.imread('../data/left.tif', cv.IMREAD_GRAYSCALE), 1024, 0, -3.5)
    right = ImageWithFeatures(cv.imread('../data/right.tif', cv.IMREAD_GRAYSCALE), 1024)
    matches = np.array(left.match(right))

    rectified = rectify(left.img, right.img, matches, verbose=True)
    disparity_w = disparity(rectified.left, rectified.right, rectified.matches, verbose=True)
    disparity = unrectify(disparity_w, rectified.h1, left.img.shape)

    plt.imshow(disparity)
    plt.show()

    cv.imwrite('disparity.png', disparity)
