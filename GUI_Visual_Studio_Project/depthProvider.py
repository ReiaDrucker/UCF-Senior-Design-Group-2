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

    def __init__(self, fov):
        super().__init__()

        self.images = [None] * 4
        self.current = 0

        self.disparity = None
        self.fov = fov
        self.baseline = 1

        self.depth = None

    # Could probably make this more generic but we don't really need to for our case
    def createInterpolatedImage(self):
        if (self.images[0] is not None) and (self.images[3] is not None):

            self.images[2] = (self.images[0] * 0.25 + self.images[3] * 1)
            self.images[2] = ((self.images[2] - self.images[2].min()) * (1/(self.images[2].max() - self.images[2].min()) * 255)).astype('uint8')

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
        new = self.images[self.current].shape

        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        rectified = disparity.rectify(*stereo)
        d_w = disparity.disparity(*stereo[:3], filter=False)
        self.disparity = disparity.unrectify(d_w, rectified.h1, stereo.left.shape)

        self.update_depth_from_disparity()
        # for now just using this approximation of focal length for the human eye (pixels)
        f = 3.2 * ((stereo.left.shape[0] * stereo.right.shape[1]) ** .5)

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

    def update_image_from_disparity(self):
        self.images[3] = ((self.disparity - self.disparity.min()) * 255.
                          / (self.disparity.max() - self.disparity.min())).astype(np.uint8)

    def update_depth_from_disparity(self):
        dims = self.images[0].shape
        L = (dims[0] * dims[1]) ** .5
        f = (L / 2) / math.tan(self.fov / 2)

        self.depth = depth.make_xyz(self.disparity, f, self.baseline)
        self.depthUpdated.emit()

    def getXYZ(self, u, v):
        if self.depth is not None:
            return depth.get_xyz(self.depth, u, v)

        return np.array([u, v, 1])

    def pixmap(self, idx):
        img = QtGui.QImage(self.images[idx].data,
                           self.images[idx].shape[1],
                           self.images[idx].shape[0],
                           self.images[idx].shape[1],
                           QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap(img)

    def current_pixmap(self):
        return self.pixmap(self.current)

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
        super().__init__(fov)

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

        self.update_image_from_disparity()

        new = self.images[self.current].shape
        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        self.update_depth_from_disparity()
        print("--- Execution time: %s seconds ---" % (time.time() - start_time))

        self.createInterpolatedImage()
        self.depthUpdated.emit()
