import cv2 as cv
import numpy as np
from collections import namedtuple

import pickle
import os
import sys

from matplotlib import pyplot as plt

from scipy.sparse import lil_matrix
from scipy.optimize import least_squares

Pose = namedtuple('Pose', 'f, R, t')
def estimate_pose(stereo, f):
    assert stereo.matches is not None

    matches = stereo.matches.astype('float64')
    matches[:,0] -= np.array([stereo.left.shape[1] / 2, stereo.left.shape[0] / 2])
    matches[:,1] -= np.array([stereo.right.shape[1] / 2, stereo.right.shape[0] / 2])

    K = np.array([
        [f, 0, 0,],
        [0, f, 0,],
        [0, 0, 1]
    ])

    E, mask = cv.findEssentialMat(matches[:,0], matches[:,1], K, cv.LMEDS)
    mask = mask.ravel()
    assert len(mask[mask == 1]) > 0

    matches = matches[mask == 1]

    _, R, t, mask = cv.recoverPose(E, matches[:,0], matches[:,1])
    mask = mask.ravel()
    assert len(mask[mask == 255]) > 0

    matches = matches[mask == 255]

    matches[:,0] += np.array([stereo.left.shape[1] / 2, stereo.left.shape[0] / 2])
    matches[:,1] += np.array([stereo.right.shape[1] / 2, stereo.right.shape[0] / 2])

    return Pose(f, R, t.ravel()), stereo._replace(matches=matches)


def triangulate(matches, pose):
    K = np.array([
        [pose.f, 0, 0,],
        [0, pose.f, 0,],
        [0, 0, 1]
    ])

    T0 = np.hstack((pose.R, pose.t.reshape(3, 1)))
    T1 = np.hstack((np.identity(3), np.zeros((3, 1))))

    P0 = np.matmul(K, T0)
    P1 = np.matmul(K, T1)

    points = cv.triangulatePoints(P0, P1, matches[:, 0].transpose(), matches[:, 1].transpose())
    return cv.convertPointsFromHomogeneous(points.transpose())

def undistort(img, pose, k0, k1):
    K = np.array([
        [pose.f, 0, stereo.left.shape[1] / 2],
        [0, pose.f, stereo.left.shape[0] / 2],
        [0, 0, 1]
    ], dtype=np.float64)

    return cv.undistort(img, K, np.array([k0, k1, 0, 0, 0]))

def plot_pose(pose, points_3d):
    ax = plt.axes(projection='3d')


    ax.scatter3D(0, 0, 0, s=100)

    ax.scatter3D(points_3d[:,0], points_3d[:,1], points_3d[:,2])

    ax.quiver(0, 0, 0, 0, 0, 1,
              length=200000, arrow_length_ratio=.005, color='red')

    ax.quiver(0, 0, 0, pose.t[0], pose.t[1], pose.t[2], arrow_length_ratio=.005)

    v = -np.matmul(pose.R, np.array([0, 0, 1]))
    print(v, np.linalg.norm(v))
    ax.quiver(pose.t[0], pose.t[1], pose.t[2], v[0], v[1], v[2],
              length=200000, arrow_length_ratio=.005, normalize=True, color='green')

    plt.show()


def improve_pose(stereo, pose):
    assert stereo.matches is not None

    matches = stereo.matches.astype('float64')
    matches[:,0] -= np.array([stereo.left.shape[1] / 2, stereo.left.shape[0] / 2])
    matches[:,1] -= np.array([stereo.right.shape[1] / 2, stereo.right.shape[0] / 2])

    n = matches.shape[0]

    r_vec, _ = cv.Rodrigues(pose.R)
    r_vec = r_vec.ravel()

    def fun(params, get_jacobian=False):
        camera_params = params[:2 * 9].reshape((2, 9))
        points_3d = params[2 * 9:].reshape((n, 3))

        ret = np.zeros((n * 2, 2))
        for cam in range(2):
            f = camera_params[cam][6]
            k1 = camera_params[cam][7]
            k2 = camera_params[cam][8]
            K = np.array([
                [f, 0, 0,],
                [0, f, 0,],
                [0, 0, 1]
            ])

            # TODO: this function returns the Jacobian,
            # so we might be able to avoid finite difference
            points_proj, J = cv.projectPoints(points_3d,
                                              camera_params[cam][:3],
                                              camera_params[cam][3:6],
                                              K, np.array([k1, k2, 0, 0, 0]))

            ret[cam * n:(cam + 1) * n] = points_proj.reshape((n, 2)) - matches[:,cam]

        return ret.ravel()

    points_3d = triangulate(matches, pose).reshape((n, 3))

    mask = points_3d[:,2] >= 0
    points_3d = points_3d[mask]
    matches = matches[mask]

    n = matches.shape[0]

    plot_pose(pose, points_3d)

    x0 = np.array([
        0, 0, 0,
        0, 0, 0,
        pose.f, 0, 0, 

        r_vec[0], r_vec[1], r_vec[2],
        pose.t[0], pose.t[1], pose.t[2],
        pose.f, 0, 0,
    ])

    x0 = np.append(np.array(x0, dtype=np.float64), points_3d.ravel())
    og = fun(x0)

    A = lil_matrix((n * 4, 2 * 9 + n * 3), dtype=int)
    for cam in range(2):
        A[cam * 2 * n:(cam + 1) * 2 * n,
          cam * 9 : (cam + 1) * 9] = 1
        for i in range(n):
            A[cam * 2 * n + i * 2 : cam * 2 * n + (i + 1) * 2,
              2 * 9 + i * 3 : 2 * 9 + (i + 1) * 3] = 1

    res = least_squares(fun, x0, jac_sparsity=A, verbose=2, x_scale='jac', ftol=1e-4, method='trf')
    plt.plot(res.fun - og)
    plt.show()

    f = (res.x[6] + res.x[15]) / 2
    R, _ = cv.Rodrigues(res.x[9:12])
    t = res.x[3:6]
    pose = pose._replace(f=f, R=R, t=t)

    distortion = np.array([
        [res.x[7], res.x[8], 0, 0, 0],
        [res.x[16], res.x[17], 0, 0, 0]
    ])

    points_3d = res.x[2 * 9:].reshape((n, 3))
    plot_pose(pose, points_3d)

    return pose, distortion

def try_loading(path):
    if not os.path.exists(path):
        print('huh')
        return None

    with open(path, 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    from matching import *
    from disparity import *

    left = cv.imread('../data/left.tif')
    right = cv.imread('../data/right.tif')

    stereo = try_loading('stereo.pkl')
    if stereo is None:
        stereo = make_stereo_pair(left, right)
        stereo = fill_matches(stereo)
        stereo = adjust_scale(stereo, 1000)
        stereo = fill_matches(stereo)

        with open('stereo.pkl', 'wb') as f:
            pickle.dump(stereo, f, pickle.HIGHEST_PROTOCOL)

    f = 3.2 * ((left.shape[0] * left.shape[1]) ** .5)
    print('Focal Length Guess:', f)
    pose, stereo = estimate_pose(stereo, f)
    print(pose)

    pose, distortion = improve_pose(stereo, pose)
    print(pose)

    stereo = rectify_calibrated(stereo, pose, distortion)

    # test = debug_frame(stereo, .5, True)
    # plt.imshow(test)
    # plt.show()

    # disparity = disparity(*stereo, filter=False, verbose=True)

    # plt.imshow(disparity)
    # plt.show()
    
