from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time
from scipy.optimize import least_squares
from math import exp

import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from depth import matching, disparity, depth

def _normalize(img):
    return ((img - img.min()) * 255. / (img.max() - img.min())).astype(np.uint8)

class DepthProvider(QtCore.QObject):
    imageChanged = QtCore.pyqtSignal()
    imageScaled = QtCore.pyqtSignal(float, float)
    depthUpdated = QtCore.pyqtSignal()

    def reset(self, fov, baseline):
        self.images = [None] * 4
        self.current = 0
        self.disparity = None
        self.fov = fov
        self.baseline = baseline
        self.principal = np.array([0, 0])
        self.disp_offset = 0
        self.depth = None

    def __init__(self, app, fov, baseline = 1):
        super().__init__()
        self.app = app
        self.reset(fov, baseline)

    def calibrate(self):
        if self.disparity is None:
            return

        dims = self.images[3].shape

        # collect an array the points we'll use for optimization
        pts = []
        for name, vec in self.app.vectorTable:
            if math.isnan(vec.measured):
                continue

            def get_point_and_disparity(pt):
                d = self.getDisp(pt.u, pt.v)
                return np.array([pt.u, pt.v, d])

            pts += [(get_point_and_disparity(vec.s),
                     get_point_and_disparity(vec.t),
                     vec.measured)]

        if len(pts) < 2:
            return

        # Parameters we're trying to optimize:
        # x[0]: focal length (pixels)
        # x[1]: baseline
        # x[2]: x-coord of principal point
        # x[3]: y-coord of principal point
        # x[4]: relative offset between x-coord of principal point in right image from left image
        #       i.e, an offset for the disparity

        side = (dims[0] * dims[1]) ** .5
        f = (side / 2) / math.tan(self.fov / 2)
        b = self.baseline
        x_0 = [f, b, -dims[1] / 2, -dims[0] / 2, 0]

        # in this case, cost is just a vector of the differences in magnitude between
        # our projected vectors and the expected "known" lengths
        # and then normalized
        def cost(x):
            def convert_to_3d(v):
                U = v[0] + x[2]
                V = v[1] + x[3]
                D = v[2] + x[4]
                return np.array([
                    U * x[1] / D,
                    V * x[1] / D,
                    x[0] * x[1] / D,
                ])

            ret = []
            for s, t, expected in pts:
                S = convert_to_3d(s)
                T = convert_to_3d(t)
                dist = (S - T)

                # signed magnitude if the points are flipped in our projection
                sign = 1
                if (d[0] < 0) != (s[0] < t[0]) or (d[1] < 0) != (s[1] < t[1]):
                    sign = -1
                dist = (sign * d.dot(d)) ** 0.5

                ret += [dist / expected - 1]

            return np.array(ret)

        # boundaries:
        radius = 100 # only vary the center points by up to 100 pixels to make this easier (TODO: should be percent)
        x_lo = [300, 0, x_0[2] - radius, x_0[3] - radius, -np.inf]
        x_hi = [np.inf, np.inf, x_0[2] + radius, x_0[3] + radius, np.inf]

        res = least_squares(cost, x_0, xtol=None, ftol=None, bounds=(x_lo, x_hi))

        print(res)
        print('final cost', cost(res.x))

        # extract the parameters from the result
        self.baseline = res.x[1]
        f = res.x[0]
        self.fov = 2 * math.atan((side / 2) / f)
        self.principal = np.array([-res.x[2], -res.x[3]])
        self.disp_offset = res.x[4]

        self.update_depth_from_disparity()

        print('baseline:', self.baseline, 'fov:', self.fov)

    def get_fov(self):
        return self.fov

    def get_baseline(self):
        return self.baseline

    def get_images(self):
        return self.images

    def set_image(self, idx, img_or_path, calculate = True):
        if type(img_or_path) == str:
            self.images[idx] = cv.imread(img_or_path, cv.IMREAD_GRAYSCALE)
        else:
            self.images[idx] = img_or_path

        if (self.images[0] is not None) and (self.images[1] is not None):
            if calculate:
                self.calculate_async()
        else:
            self.show(idx)

    def get_disparity(self):
        return self.disparity

    def set_disparity(self, disparity):
        self.disparity = disparity
        self.update_depth_from_disparity()

    def should_calculate(self):
        return (self.images[3] is None) and (self.images[0] is not None) and (self.images[1] is not None)

    def calculate(self):
        # TODO: detect/display errors
        old = self.images[self.current].shape
        stereo = matching.make_stereo_pair(*self.images)
        stereo = matching.fill_matches(stereo)
        stereo = matching.adjust_scale(stereo, 1000)
        # stereo = matching.surface_blur(stereo, 50)
        stereo = matching.fill_matches(stereo)

        self.images[:2] = [stereo.left, stereo.right]

        rectified = disparity.rectify(*stereo)
        d_w = disparity.disparity(*stereo[:3], filter=False)
        self.disparity = disparity.unrectify(d_w, rectified.h1, stereo.left.shape)
        self.update_images_from_disparity()

        new = self.images[self.current].shape
        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        self.principal = np.array([disparity.shape[1] / 2, disparity.shape[0] / 2])

        self.update_depth_from_disparity()

    def calculate_async(self):
        class Runnable(QtCore.QRunnable):
            def __init__(self, provider):
                super().__init__()
                self.provider = provider

            def run(self):
                self.provider.calculate()

        pool = QtCore.QThreadPool.globalInstance()

        r = Runnable(self)
        pool.start(r)

    def update_images_from_disparity(self):
        self.images[3] = _normalize(self.images[3])

        self.images[2] = (self.images[0] * 0.25 + self.images[3] * 1)
        self.images[2] = _normalize(self.images[2])

    def update_depth_from_disparity(self):
        dims = self.images[0].shape
        L = (dims[0] * dims[1]) ** .5
        f = (L / 2) / math.tan(self.fov / 2)
        print('focal length (px):', f)

        self.depth = depth.make_xyz(self.disparity, f, self.baseline)
        self.depthUpdated.emit()

    def getXYZ(self, u, v):
        if self.depth is not None:
            dims = self.images[0].shape
            L = (dims[0] * dims[1]) ** .5
            f = (L / 2) / math.tan(self.fov / 2)
            disp = depth.get_xyz(self.disparity, u, v) + self.disp_offset
            return np.array([
                (u - self.principal[0]) * self.baseline / disp,
                (v - self.principal[1]) * self.baseline / disp,
                f * self.baseline / disp,
                disp
            ])

        return np.array([u, v, 1, 0])

    def getDisp(self, u, v):
        # TODO
        # should probably rename/move depth.get_xyz to util.image_interp,
        # as it can clearly do more than just interp depth
        return depth.get_xyz(self.disparity, u, v)

    def pixmap(self, idx):
        img = QtGui.QImage(self.images[idx].data,
                           self.images[idx].shape[1],
                           self.images[idx].shape[0],
                           self.images[idx].shape[1],
                           QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap(img)

    def current_pixmap(self):
        return self.pixmap(self.current)

    def show(self, idx):
        if idx < len(self.images) and self.images[idx] is not None:
            self.current = idx
            self.imageChanged.emit()

import depth_algo
import math

class DepthProvider2(DepthProvider):
    def __init__(self, app, fov, baseline = 1):
        super().__init__(app, fov, baseline)

    def calculate(self):
        start_time = time.time()
        #print(start_time)

        old = self.images[self.current].shape

        stereo = (depth_algo.ImagePairBuilder()
                       .set_target_scale(2000)
                       .build()
                       .load_images(self.images[0], self.images[1])
                       .fill_matches())

        pose = depth_algo.CameraPose(stereo, self.fov)
        stereo.rectify(pose)

        matches = pose.get_matches()

        dx = matches[:,0,0] - matches[:,1,0]
        q1, q3 = np.quantile(dx, [.25, .75])
        iqr = q3 - q1
        lo = math.floor(q1 - iqr * 1.5)
        hi = math.ceil(q3 + iqr * 1.5)

        cloud = (depth_algo.PointCloudBuilder()
                      .set_matcher(depth_algo.PointCloudMatcherType.LOCAL_EXP)
                      .set_gssim_consts([.9, .1, .2])
                      .set_gssim_patch_size(5)
                      .set_min_disp(lo)
                      .set_max_disp(hi)
                      .build()
                      .load_stereo(stereo))
        d_w = cloud.get_disparity()

        self.disparity = pose.unrectify(d_w, 0)
        self.images[:2] = [pose.unrectify(stereo.get_image(i), i) for i in range(2)]

        self.update_images_from_disparity()

        new = self.images[self.current].shape
        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        self.update_depth_from_disparity()
        print("--- Execution time: %s seconds ---" % (time.time() - start_time))

        self.depthUpdated.emit()
