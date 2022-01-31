import os, sys
import cv2 as cv
import numpy as np
import math
import random
from collections import namedtuple
from matplotlib import pyplot as plt
import matplotlib

if __package__:
    from . import util
else:
    import util

def _rescale(img, L):
    '''
    Resize the image to fit in an LxL box
    '''
    s = min(L / img.shape[0], L / img.shape[1])
    return cv.resize(img, np.int0((img.shape[1] * s, img.shape[0] * s)))

StereoPair = namedtuple('StereoPair', 'left, right, matches')
def make_stereo_pair(left, right, L = None):
    '''
    Make a stereo pair for future operations
    '''
    if L is not None:
        left = _rescale(left, L)
        right = _rescale(right, L)

    return StereoPair(left, right, None)

ImageFeatures = namedtuple('ImageFeatures', 'kp, des')
def _find_features(img):
    '''
    Find the features in an image using ORB tracker
    '''
    orb = cv.ORB_create(nfeatures=100000)
    kp = orb.detect(img, None)
    kp, des = orb.compute(img, kp)
    return ImageFeatures(kp, des)

def _pts_from_match(match, left_kp, right_kp):
    '''
    Convert orb feature to image coordinates
    '''
    return (np.int0(left_kp[match.queryIdx].pt),
            np.int0(right_kp[match.trainIdx].pt))

def fill_matches(stereo):
    '''
    Find matching features in each image and append them to the StereoPair
    '''
    feat_l = _find_features(stereo.left)
    feat_r = _find_features(stereo.right)

    # Match descriptors.
    bf = cv.BFMatcher(cv.NORM_HAMMING)
    matches = bf.knnMatch(feat_l.des, feat_r.des, k = 2)

    good = []
    for m,n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    # Sort them in the order of their distance (between feature vectors, not points).
    good = sorted(good, key = lambda x:x.distance)
    good = [_pts_from_match(match, feat_l.kp, feat_r.kp) for match in good]
    good = np.array(good).reshape(len(good), 2, 2)
    return stereo._replace(matches=good)

def remove_match_outliers(matches):
    '''
    For debugging.
    Remove outliers based on length.
    '''
    u = matches[:,0]
    v = matches[:,1]
    d = np.linalg.norm(u - v, axis=1)
    q1 = np.quantile(d, .25)
    q3 = np.quantile(d, .75)
    iqr = q3 - q1
    lo = q1 - iqr * 1.5
    hi = q3 + iqr * 1.5
    mask = (lo < d) & (d < hi)
    u = u[mask == 1]
    v = v[mask == 1]
    return np.c_[u, v].reshape(u.shape[0], 2, 2)

def adjust_scale(stereo, L):
    assert stereo.matches is not None

    u = stereo.matches[:,0]
    v = stereo.matches[:,1]

    d = v[:,0] - u[:,0]
    q = np.percentile(d, [.25, .75])

    low_x = q[0] - (q[1] - q[0]) * 1.5

    c1 = np.mean(u[:,1])
    c2 = np.mean(v[:,1])

    d1 = np.mean(np.linalg.norm(u - c1, axis=1) ** 2) ** .5
    d2 = np.mean(np.linalg.norm(v - c2, axis=1) ** 2) ** .5

    h1 = np.array([
        [1, 0, 0],
        [0, 1, -c1],
        [0, 0, d1]
    ])

    h2 = np.array([
        [1, 0, -low_x],
        [0, 1, -c2],
        [0, 0, d2]
    ])

    h1, h2 = util.correct_homographies((h1, h2), (stereo.left.shape, stereo.right.shape), (L, L))

    left = cv.warpPerspective(stereo.left, h1, (L, L), flags=cv.INTER_NEAREST)
    right = cv.warpPerspective(stereo.right, h2, (L, L), flags=cv.INTER_NEAREST)

    u = util.warp_points(u, h1)
    v = util.warp_points(v, h2)

    c1 = np.mean(u, axis=0)
    c2 = np.mean(v, axis=0)

    return StereoPair(left, right, np.c_[u, v].reshape((u.shape[0], 2, 2)))

def surface_blur(stereo, sigma):
    stereo = stereo._replace(left = cv.bilateralFilter(stereo.left, -1, sigma, sigma))
    stereo = stereo._replace(right = cv.bilateralFilter(stereo.right, -1, sigma, sigma))
    return stereo

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

def debug_video(stereo, video_path, fps, seconds):
    '''
    For debugging.
    Generate a video from a series of debug frames.
    '''
    fourcc = cv.VideoWriter_fourcc(*'MP42')

    shape = (
        min(stereo.left.shape[0], stereo.right.shape[0]),
        min(stereo.left.shape[1], stereo.right.shape[1])
    )

    video = cv.VideoWriter(video_path,
                           fourcc,
                           fps,
                           (shape[1], shape[0]),
                           True)

    for i in range(fps * seconds):
        z = (math.sin(i * 2 * math.pi / fps / seconds) + 1) / 2
        frame = debug_frame(stereo, z)
        video.write(frame)
    video.release()

def alt_debug_frame(stereo):
    fig = plt.figure(figsize=(10,5))
    L = fig.add_subplot(121)
    R = fig.add_subplot(122)
    L.imshow(stereo.left)
    L.axis('off')
    R.imshow(stereo.right)
    R.axis('off')

    matches = stereo.matches
    print(matches.shape)

    fig.canvas.draw()
    transFig = fig.transFigure.inverted()
    for i in random.sample(range(matches.shape[0]), 100):
        u = matches[i][0]
        v = matches[i][1]

        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)

        L.scatter(u[0], u[1], s=20, color=color)
        R.scatter(v[0], v[1], s=20, color=color)

        u2 = transFig.transform(L.transData.transform(u))
        v2 = transFig.transform(R.transData.transform(v))

        line = matplotlib.lines.Line2D((u2[0], v2[0]),
                                       (u2[1], v2[1]),
                                       transform=fig.transFigure,
                                       color=color)
        fig.lines.append(line)

    plt.show()

if __name__ == '__main__':
    left = cv.imread('../data/left.tif')
    right = cv.imread('../data/right.tif')

    stereo = make_stereo_pair(left, right)
    stereo = fill_matches(stereo)
    stereo = adjust_scale(stereo, 1000)
    stereo = fill_matches(stereo)
    stereo = stereo._replace(matches=remove_match_outliers(stereo.matches))
    stereo = adjust_scale(stereo, 1000)

    alt_debug_frame(stereo)

    frame = debug_frame(stereo, .5, lines=True)
    plt.imshow(frame)
    plt.show()

    if len(sys.argv) > 1:
        assert '.avi' in sys.argv[1]
        debug_video(stereo, sys.argv[1], 24, 10)
