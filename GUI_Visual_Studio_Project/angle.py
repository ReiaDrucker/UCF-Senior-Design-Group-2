from PyQt5 import QtCore, QtGui, QtWidgets

import math

from dataTable import DataTableRow

class Angle(DataTableRow):
    def __init__(self, a, b):
        super().__init__()

        def updater(key):
            @QtCore.pyqtSlot()
            def func():
                self.__setattr__(key, self.sender())
                self.recalculate()
            return func

        self['a'] = self.create_field(a, editable=False)
        a.dataChanged.connect(updater('a'))
        a.deleted.connect(self.delete)

        self['b'] = self.create_field(b, editable=False)
        b.dataChanged.connect(updater('b'))
        b.deleted.connect(self.delete)

        self['angle'] = self.create_field(0, float, editable=False)

        self.recalculate()

        self['D'] = QtWidgets.QPushButton('Delete')
        self['D'].clicked.connect(self.delete)

    def recalculate(self):
        c = self.a.dot(self.b) / self.a.dist / self.b.dist
        self.angle = math.acos(c) * 180 / math.pi

    def serialize(self):
        return self.a.name, self.b.name
