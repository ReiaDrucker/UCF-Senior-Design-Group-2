from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from depth import matching, disparity, depth

class DepthProvider(QtCore.QObject):
    imageChanged = QtCore.pyqtSignal()
    imageScaled = QtCore.pyqtSignal(float, float)
    depthUpdated = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.images = [None] * 2
        self.stereo = None
        self.current = 0
        self.depth = None

        # self.depthUpdated.connect(self.debug)

    def calculate(self):
        # TODO: detect/display errors
        old = self.images[self.current].shape
        stereo = matching.make_stereo_pair(*self.images)
        stereo = matching.fill_matches(stereo)
        stereo = matching.adjust_scale(stereo, 1000)
        # stereo = matching.surface_blur(stereo, 50)
        stereo = matching.fill_matches(stereo)

        self.debug_frame = matching.debug_frame(stereo, 0.5)

        self.images = [stereo.left, stereo.right]
        new = self.images[self.current].shape

        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        rectified = disparity.rectify(*stereo)
        d_w = disparity.disparity(*stereo[:3], filter=False)
        self.d = disparity.unrectify(d_w, rectified.h1, stereo.left.shape)

        # for now just using this approximation of focal length for the human eye (pixels)
        f = 3.2 * ((stereo.left.shape[0] * stereo.right.shape[1]) ** .5)

        self.depth = depth.make_xyz(self.d, f, 1)
        self.depthUpdated.emit()

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
        print(self.d.shape, np.min(self.d), np.max(self.d))

        fig, ax = plt.subplots(2)
        ax[0].imshow(self.d)
        ax[1].imshow(self.debug_frame)
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

    def set_image(self, idx, path, calculate = True):
        self.images[idx] = cv.imread(path, cv.IMREAD_GRAYSCALE)

        if (self.images[0] is not None) and (self.images[1] is not None):
            if calculate:
                self.calculate_async()
        else:
            self.show(idx)

    def reset(self):
        self.images = [None] * 2

    def show(self, idx):
        if idx < len(self.images) and self.images[idx] is not None:
            self.current = idx
            self.imageChanged.emit()
