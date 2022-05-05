from PyQt5 import QtCore, QtGui, QtWidgets
from MagPopup import *

from dataTable import DataTableRow
import math
import numpy as np

class Vector(DataTableRow):
    # Signal to check if any data in the vector has been changed.
    dataChanged = QtCore.pyqtSignal()
    sourceChanged = QtCore.pyqtSignal()

    def __init__(self, s, t):
        super().__init__()

        # Updates data upon table cell change.
        def updater(key):
            @QtCore.pyqtSlot()
            def func():
                self.__setattr__(key, self.sender())
                self.recalculate()
            return func


        # Create column headers.
        self['s'] = self.create_field(s, editable=False)
        s.dataChanged.connect(updater('s'))
        s.sourceChanged.connect(self.sourceChanged.emit)

        s.deleted.connect(self.delete)

        self['t'] = self.create_field(t, editable=False)
        t.dataChanged.connect(updater('t'))

        t.sourceChanged.connect(self.sourceChanged.emit)

        t.deleted.connect(self.delete)

        for field in ['dx', 'dy', 'dz']:
            self[field] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)

        # Magnitude field.
        self['dist'] = self.create_field(0, float, lambda x: f'{x:.2f}', editable=False)


        # Field for inputting known lengths
        self['measured'] = self.create_field(math.nan, float, lambda x: f'{x:.2f}', editable=True)
        self['measured'].dataChanged.signal.connect(self.dataChanged.emit)
        self['measured'].dataChanged.signal.connect(self.sourceChanged.emit)

        self.recalculate()

        # Place delete button next to every vector row.
        self['D'] = QtWidgets.QPushButton('Delete')
        self['D'].clicked.connect(self.delete)

    def to_vec(self):
        return np.array([self.dx, self.dy, self.dz])


    # Recalculates vector properties.
    def recalculate(self):
        self.dx = self.t.x - self.s.x
        self.dy = self.t.y - self.s.y
        self.dz = self.t.z - self.s.z

        dist = (self.dx ** 2 + self.dy ** 2 + self.dz ** 2) ** .5
        self.dist = dist

        self.dataChanged.emit()

    def __str__(self):
        return f'{self.name}: <{self.dx:.1f}, {self.dy:.1f}, {self.dz:.1f}>'

    def serialize(self):
        return self.s.name, self.t.name
