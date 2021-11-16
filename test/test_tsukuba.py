# TODO: use pytest instead
# TODO: load data from data script
from matplotlib import pyplot as plt
import cv2 as cv
import numpy as np

from multiprocessing import Pool

import os, sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Add depth module to the python path
sys.path.append(ROOT_DIR)

TSUKUBA_DIR = os.path.join(ROOT_DIR, 'data/tsukuba/NewTsukubaStereoDataset')
DISPARITY_DIR = os.path.join(TSUKUBA_DIR, 'groundtruth/disparity_maps/left')
LEFT_DIR = os.path.join(TSUKUBA_DIR, 'illumination/daylight/left')
RIGHT_DIR = os.path.join(TSUKUBA_DIR, 'illumination/daylight/right')

def grab_data(base, pattern, idx):
    fname = sorted(os.listdir(base))[idx]
    fname = os.path.join(base, fname)
    assert os.path.exists(fname)
    assert('.png' in fname) # TODO: support xml
    return cv.imread(fname)

def calc_disparity(left, right, verbose=False):
    from depth.matching import ImageWithFeatures
    from depth.disparity import disparity_uncalibrated

    left = cv.cvtColor(left, cv.COLOR_BGR2GRAY)
    right = cv.cvtColor(right, cv.COLOR_BGR2GRAY)

    left = ImageWithFeatures(left, 640)
    right = ImageWithFeatures(right, 640)

    return disparity_uncalibrated(left, right, verbose=verbose)

def grab_all_data(idx):
    left = grab_data(LEFT_DIR, 'daylight_L', idx)
    right = grab_data(RIGHT_DIR, 'daylight_R', idx)
    disp = grab_data(DISPARITY_DIR, 'disparity_L', idx)
    disp = cv.cvtColor(disp, cv.COLOR_BGR2GRAY)

    return (left, right, disp)

def check_accuracy(idx, center = 16, thresh = 0.2, verbose=False):
    left, right, disp = grab_all_data(idx)

    mix = np.uint8(np.add(np.multiply(left, .5), np.multiply(right, .5)))
    d_est = calc_disparity(left, right, verbose=verbose)

    filtered = d_est / disp
    filtered = (filtered > center / (1 + thresh)) & (filtered < center / (1 - thresh))

    if verbose:
        f, axarr = plt.subplots(2, 3)
        axarr[0,0].imshow(mix)
        axarr[1,0].imshow(disp)
        axarr[0,1].imshow(d_est)
        axarr[1,1].imshow(d_est / disp)

        hist_data = (d_est / disp).flatten()
        hist_data[hist_data < -1e15] = -1e15
        hist_data[hist_data > 1e15] = 1e15
        axarr[0,2].hist(hist_data, 20)
        axarr[1,2].imshow(filtered)
        plt.show()

    return len(filtered[filtered == True]) / len(filtered.flatten())

if __name__ == '__main__':
    def batch_accuracy(sample):
        with Pool(12) as p:
            return p.map(check_accuracy, sample)

    acc = batch_accuracy(range(1800))
    plt.hist(acc, bins=20)
    plt.show()

    print('accuracy:', np.mean(acc))
    worst = sorted(enumerate(acc), key = lambda x: x[1])[:10]
    print('bottom', len(worst))
    for idx, acc in worst:
        print(idx, acc)

    print(check_accuracy(worst[0][0], verbose=True))
    
