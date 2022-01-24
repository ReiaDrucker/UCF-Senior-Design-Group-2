from PyQt5 import QtCore, QtGui, QtWidgets

import math
import numpy as np

from dataTable import DataTableRow

class Point(DataTableRow):
    dataChanged = QtCore.pyqtSignal()
    blocked = False

    def __init__(self, depthProvider, u = 0, v = 0):
        super().__init__()

        self.depthProvider = depthProvider
        self.depthProvider.depthUpdated.connect(self.recast)

        for field in 'uv':
            self[field] = self.create_field(0, float)
            self[field].dataChanged.signal.connect(self.recast)
            self[field].dataChanged.signal.connect(self.dataChanged.emit)

        for field in 'xyz':
            self[field] = self.create_field(0, float)
            self[field].dataChanged.signal.connect(self.reproject)
            self[field].dataChanged.signal.connect(self.dataChanged.emit)

        self.z = 1
        self.u = u
        self.v = v

        self['D'] = QtWidgets.QPushButton('Delete')
        self['D'].clicked.connect(self.delete)

    @QtCore.pyqtSlot()
    def reproject(self):
        if self.blocked:
            return
        self.blocked = True

        # TODO: handle camera params (position, rotation, focal length)
        f = 1
        self.u = self.x * f / self.z
        self.v = self.y * f / self.z

        self.blocked = False

    @QtCore.pyqtSlot()
    def recast(self):
        if self.blocked:
            return
        self.blocked = True

        # TODO: handle camera params (positon, rotation, focal length)
        self.x, self.y, self.z = self.depthProvider.getXYZ(self.u, self.v)

        self.blocked = False
