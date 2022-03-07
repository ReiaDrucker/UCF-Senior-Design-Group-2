#!/bin/env python
# TODO: pytest

from copy import deepcopy

import depth_algo as depth
import matplotlib.pyplot as plt

import cv2 as cv
import numpy as np
import math

import argparse
import code

from collections import namedtuple

with_timing = False
try:
    from codetiming import Timer
    with_timing = True
except:
    print('No timing available, install codetiming if you want to measure time elapsed')

config = {
    'verbose': True
}

StereoPair = namedtuple('StereoPair', 'left, right, matches')
def debug_frame(stereo, z, lines = False):
    '''
    For debugging.
    Generate a frame interopolating between the left and right images.
    '''
    def _lerp(a, b, x):
        return np.add(np.multiply(a, x), np.multiply(b, 1 - x))
    def _sigmoid(x):
        return 1 / (1 + math.exp(-x))

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

def matching(l_path, r_path):
    left = cv.imread(l_path, cv.IMREAD_GRAYSCALE)
    right = cv.imread(r_path, cv.IMREAD_GRAYSCALE)

    stereo = (depth.ImagePairBuilder()
              .set_target_scale(2000)
              .build()
              .load_images(left, right)
              .fill_matches())

    print('\tMatches shape:', stereo.get_matches().shape)

    return stereo

def rectify(stereo, fov):
    stereo_ = deepcopy(stereo)
    pose = depth.CameraPose(stereo_, fov * math.pi / 180)

    # pose.refine()
    # print(pose)

    stereo_.rectify(pose)

    matches = pose.get_matches()
    print('\tFiltered matches shape:', matches.shape)

    return stereo_, matches

def guess_disparity_range(matches):
    n = matches.shape[0]
    dx = np.array([matches[i,0,0] - matches[i,1,0] for i in range(n)])
    print('\tDisparity statistics from matches (min, median, max):', dx.min(), np.median(dx), dx.max())

    q1,q3 = np.quantile(dx, [.25, .75])
    iqr = q3 - q1
    lo = math.floor(q1 - iqr * 1.5)
    hi = math.ceil(q3 + iqr * 1.5)

    return lo, hi

def disparity(stereo, lo, hi):
    # TODO: do a better job detecting min/max disparities
    cloud = (depth.PointCloudBuilder()
             .set_matcher(depth.PointCloudMatcherType.LOCAL_EXP)
             .set_gssim_consts([.9, .1, .2])
             .set_gssim_patch_size(5)
             .set_min_disp(lo)
             .set_max_disp(hi)
             .build()
             .load_stereo(stereo))

    return cloud.get_disparity(), cloud

def focal_grid(n = 25):
    w = int(n ** .5)
    fig, ax = plt.subplots((n + w - 1) // w, w)

    s = 30
    t = 180
    step = (t - s) / n

    for i in range(n):
        x = s + step * i
        try:
            stereo_, pose_ = rectify(stereo, x)
            right = stereo_.get_image(1)
            ax[i // w, i % w].imshow(right)
            ax[i // w, i % w].set_title('fov: {}'.format(x))
        except:
            pass

    plt.show()

def guess_from_gssim_volume(vol):
    vol2 = np.vstack(([np.ones(vol.shape[1:]) * np.inf], vol))
    return np.nanargmin(vol2, axis=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate and save point cloud disparity')

    parser.add_argument('l_path', type=str, help='Left image path')
    parser.add_argument('r_path', type=str, help='Right image path')
    parser.add_argument('--fov', dest='fov', type=int, default=120, help='Estimated FOV for rectification')
    parser.add_argument('--min_disp', dest='min_disp', type=int, default=None,
                        help='Lower end of disparity search range')
    parser.add_argument('--max_disp', dest='max_disp', type=int, default=None,
                        help='Upper end of disparity search range')
    parser.add_argument('--no-rect', dest='no_rect', action='store_true', help='Skip rectification')
    parser.add_argument('-i', dest='interactive', action='store_true', help='Open an interactive session before exiting')

    args = parser.parse_args()

    timer = None
    if with_timing:
        timer = Timer('total')
        timer.start()

    print('\nMATCHING...')
    stereo = matching(args.l_path, args.r_path)

    if args.interactive:
        code.interact(local=dict(globals(), **locals()))
    else:
        matches = None
        if args.no_rect:
            matches = stereo.get_matches()
        else:
            print('\nRECTIFICATION...')
            stereo, matches = rectify(stereo, args.fov)

        left = stereo.get_image(0)
        right = stereo.get_image(1)
        cv.imwrite('rgb.png', left)
        frame = debug_frame(StereoPair(left, right, matches), 0.5, True)

        lo, hi = args.min_disp, args.max_disp
        if lo is None or hi is None:
            if lo != hi:
                print('Warning: Please set both of max_disp and min_disp.')

            print('\nGUESSING DISPARITY RANGE...')
            lo, hi = guess_disparity_range(matches)
        else:
            print('\nUSING SELECTED DISPARITY RANGE')
        print('\tDisparity range:', lo, hi)

        print('\nDISPARITY...')
        disp, cloud = disparity(stereo, lo, hi)

        if with_timing:
            timer.stop()

        np.save('disp', disp)
        plt.hist(disp, bins=20)
        plt.show()
        print('\tOutput disparity range:', disp.min(), disp.max())
        plt.imshow(disp, cmap='gray')
        plt.show()

