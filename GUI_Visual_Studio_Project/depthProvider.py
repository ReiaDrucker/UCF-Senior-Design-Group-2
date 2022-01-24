from PyQt5 import QtCore, QtGui, QtWidgets

import cv2 as cv
import matplotlib.pyplot as plt

from depth import matching, disparity

class DepthProvider(QtCore.QObject):
    imageChanged = QtCore.pyqtSignal()
    imageScaled = QtCore.pyqtSignal(float, float)

    def __init__(self):
        super().__init__()

        self.images = [None] * 2
        self.stereo = None
        self.current = 0

    def calculate(self):
        old = self.images[self.current].shape
        stereo = matching.make_stereo_pair(*self.images)
        stereo = matching.fill_matches(stereo)
        stereo = stereo._replace(matches=matching.remove_match_outliers(stereo.matches))
        stereo = matching.adjust_scale(stereo, 1000)
        # stereo = matching.surface_blur(stereo, 50)
        stereo = matching.fill_matches(stereo)
        stereo = stereo._replace(matches=matching.remove_match_outliers(stereo.matches))

        self.images = [stereo.left, stereo.right]
        new = self.images[self.current].shape

        self.imageScaled.emit(new[1] / old[1], new[0] / old[0])
        self.imageChanged.emit()

        rectified = disparity.rectify(*stereo)
        self.debug_frame = matching.debug_frame(matching.StereoPair(rectified.left, rectified.right, rectified.matches), .5, lines=True)

    
        d_w = disparity.disparity(*rectified[:3], filter=False)
        self.d = disparity.unrectify(d_w, rectified.h1, stereo.left.shape)

    def calculate_async(self):
        class Signaller(QtCore.QObject):
            signal = QtCore.pyqtSignal()

        class Runnable(QtCore.QRunnable):
            def __init__(self, provider):
                super().__init__()
                self.done = Signaller()
                self.provider = provider

            def run(self):
                self.provider.calculate()
                self.done.signal.emit()

        pool = QtCore.QThreadPool.globalInstance()

        r = Runnable(self)
        r.done.signal.connect(self.debug)
        pool.start(r)

    def debug(self):
        plt.imshow(self.d)
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

    def set_image(self, idx, path):
        self.images[idx] = cv.imread(path, cv.IMREAD_GRAYSCALE)

        if (self.images[0] is not None) and (self.images[1] is not None):
            self.calculate_async()
        else:
            self.show(idx)

    def show(self, idx):
        if self.images[idx] is not None:
            self.current = idx
            self.imageChanged.emit()
