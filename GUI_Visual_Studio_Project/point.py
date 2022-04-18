from PyQt5 import QtCore, QtGui, QtWidgets

import math
import numpy as np

from dataTable import DataTableRow

class Point(DataTableRow):
    # Signal to check if any data in the point has been changed.
    dataChanged = QtCore.pyqtSignal()
    sourceChanged = QtCore.pyqtSignal()
    blocked = False

    def __init__(self, depthProvider, u = 0, v = 0):
        super().__init__()

        # Bring the depthProvider into the point.
        self.depthProvider = depthProvider
        self.depthProvider.depthUpdated.connect(self.recast)

        # Initialize column headers.
        for field in 'uv':
            self[field] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)
            self[field].dataChanged.signal.connect(self.recast)
            self[field].dataChanged.signal.connect(self.dataChanged.emit)
            self[field].dataChanged.signal.connect(self.sourceChanged.emit)

        for field in 'dxyz':
            self[field] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)
            self[field].dataChanged.signal.connect(self.reproject)
            self[field].dataChanged.signal.connect(self.dataChanged.emit)

        self.z = 1
        self.u = u
        self.v = v

        # Place delete button next to every point row.
        self['D'] = QtWidgets.QPushButton('Delete')
        self['D'].clicked.connect(self.delete)

    # Reproject point position.
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

    # Recast point position.
    @QtCore.pyqtSlot()
    def recast(self):
        if self.blocked:
            return
        self.blocked = True

        # TODO: handle camera params (positon, rotation, focal length)
        self.x, self.y, self.z, self.d = self.depthProvider.getXYZ(self.u, self.v)

        self.blocked = False

    def __str__(self):
        return f'{self.name}: <{self.x:.1f}, {self.y:.1f}, {self.z:.1f}>'

    def serialize(self):
        return self.u, self.v
