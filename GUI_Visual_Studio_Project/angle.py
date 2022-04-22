from PyQt5 import QtCore, QtGui, QtWidgets

import math

from dataTable import DataTableRow

class Angle(DataTableRow):
    def __init__(self, a, b):
        super().__init__()

        # Updates data upon table cell change.
        def updater(key):
            @QtCore.pyqtSlot()
            def func():
                self.__setattr__(key, self.sender())
                self.recalculate()
            return func

        # Create column headers.
        self['a'] = self.create_field(a, editable=False)
        a.dataChanged.connect(updater('a'))
        a.deleted.connect(self.delete)

        self['b'] = self.create_field(b, editable=False)
        b.dataChanged.connect(updater('b'))
        b.deleted.connect(self.delete)

        self['angle'] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)

        self.recalculate()

        self['xy'] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)
        self['xz'] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)
        self['yz'] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)

        # Place delete button next to angle point row.
        self['D'] = QtWidgets.QPushButton('Delete')
        self['D'].clicked.connect(self.delete)

    # Recalculates angle value.
    def recalculate(self):
        c = self.a.dot(self.b) / self.a.rawMagnitude / self.b.rawMagnitude
        self.angle = math.acos(c) * 180 / math.pi

    def serialize(self):
        return self.a.name, self.b.name
