from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time

import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from depth import matching, disparity, depth

class DepthProvider(QtCore.QObject):
    imageChanged = QtCore.pyqtSignal()
    imageScaled = QtCore.pyqtSignal(float, float)
    depthUpdated = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.images = [None] * 4
        self.current = 0
        self.depth = None

        # depthUpdated.connect(debug)

    def should_calculate(self):
        return (self.images[3] is None) and (self.images[0] is not None) and (self.images[1] is not None)

    def get_images(self):
        return self.images

    def get_depth(self):
        return self.depth

    def calculate(self):
        # TODO: detect/display errors
        old = self.images[self.current].shape
        stereo = matching.make_stereo_pair(*self.images)
        stereo = matching.fill_matches(stereo)
        stereo = matching.adjust_scale(stereo, 1000)
        # stereo = matching.surface_blur(stereo, 50)
        stereo = matching.fill_matches(stereo)

        # debug_frame = matching.debug_frame(stereo, 0.5)

        self.images[:2] = [stereo.left, stereo.right]
        new = self.images[self.current].shape

        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        rectified = disparity.rectify(*stereo)
        d_w = disparity.disparity(*stereo[:3], filter=False)
        d = disparity.unrectify(d_w, rectified.h1, stereo.left.shape)

        # for now just using this approximation of focal length for the human eye (pixels)
        f = 3.2 * ((stereo.left.shape[0] * stereo.right.shape[1]) ** .5)

        self.depth = depth.make_xyz(d, f, 1)
        depthUpdated.emit()

    def getXYZ(self, u, v):
        if self.depth is not None:
            return depth.get_xyz(self.depth, u, v)

        return np.array([u, v, 1])

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

    def debug(self):
        print(d.shape, np.min(d), np.max(d))

        fig, ax = plt.subplots(2)
        ax[0].imshow(d)
        ax[1].imshow(debug_frame)
        plt.show()

    def pixmap(self, idx):
        img = QtGui.QImage(self.images[idx].data,
                           self.images[idx].shape[1],
                           self.images[idx].shape[0],
                           self.images[idx].shape[1],
                           QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap(img)

    def current_pixmap(self):
        return self.pixmap(self.current)

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

    def set_depth(self, depth):
        self.depth = depth
        self.depthUpdated.emit()

    def reset(self):
        self.images = [None] * 4

    def show(self, idx):
        if idx < len(self.images) and self.images[idx] is not None:
            self.current = idx
            self.imageChanged.emit()

import depth_algo
import math

class DepthProvider2(DepthProvider):
    def __init__(self, fov):
        super().__init__()
        self.fov = fov

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
        d = cloud.get_disparity()

        d = pose.unrectify(d, 0)
        self.images[:2] = [pose.unrectify(stereo.get_image(i), i) for i in range(2)]

        disparity_scaled = ((d - d.min()) * 255. / (d.max() - d.min())).astype(np.uint8)
        self.images[3] = disparity_scaled

        new = self.images[self.current].shape
        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        L = (new[0] * new[1]) ** .5
        f = (L / 2) / math.tan(self.fov / 2)

        self.depth = depth.make_xyz(d, f, 1)
        print("--- Execution time: %s seconds ---" % (time.time() - start_time))
        self.depthUpdated.emit()
