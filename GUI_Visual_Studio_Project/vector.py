from PyQt5 import QtCore, QtGui, QtWidgets
from MagPopup import *


from dataTable import DataTableRow

class Vector(DataTableRow):
    dataChanged = QtCore.pyqtSignal()

    def __init__(self, s, t, pd):
        super().__init__()

        def updater(key):
            @QtCore.pyqtSlot()
            def func():
                self.__setattr__(key, self.sender())
                self.recalculate()
            return func

        self.pdRef = pd

        self['s'] = self.create_field(s, editable=False)
        s.dataChanged.connect(updater('s'))
        s.deleted.connect(self.delete)

        self['t'] = self.create_field(t, editable=False)
        t.dataChanged.connect(updater('t'))
        t.deleted.connect(self.delete)

        for field in ['dx', 'dy', 'dz']:
            self[field] = self.create_field(0, float, lambda x: f'{x:.1f}', editable=False)

        # Magnitude field.
        distItem = self.create_field(0, float, lambda x: f'{x:.2f}', editable=True)
        distItem.dataChanged.signal.connect(self.changeMag)
        self['dist'] = distItem

        self.prevDist = 0

        self.recalculate()

        self['D'] = QtWidgets.QPushButton('Delete')
        self['D'].clicked.connect(self.delete)

        # Grab a pointer to the depth Provider when we initialize
        # This is technically a waste of memory but it works and is easy and probably won't be an issue
        self.depthProviderRef = s.depthProvider;

    # Calculates percent of magnitude change and re-scales other vectors.
    def changeMag(self):
        if (self.prevDist != 0 and self.prevDist != self.dist and self.pdRef.drawStuff):
            percent = (self.dist/self.prevDist) * 100

            # When you edit the magnitude, the vector display is toggled off
            #   and editing for the tables is turned off.
            # Hard to tell currently if I have to modify anything since this isn't done.
            # Note: If you change data in the point table, this will toggle vector display and point editing.
            #   since that changes the magnitude.
            # msg = QtWidgets.QMessageBox()
            # #msg.setWindowTitle("Re-scaling Magnitudes. Please wait...")
            # msg.setText("Re-scaling Magnitudes. Please wait...")
            # msg.setIcon(QtWidgets.QMessageBox.Information)
            # #msg.buttonClicked.connect(print("Test"))
            # #msg.setStandardButtons()
            # msg.exec_()

            # test = MagPopup()
            # test.exec()

            # x = msg.exec_()
            # print(x)
            # if x == 1024:
            #     print("Test")

            self.pdRef.toggleDraw()

            # Issue here being that while depth is being calculated all the points update to their intermediary values maybe don't connect until that is done
            # Shouldn't be able to plot anything until after that is done anyways so probabbly not a big deal, make sure everything is disabled until depth is calculated
            # Can't test or run anything until this is setup

            #print(self.depthProviderRef.depth)
            # Need to enable some sort of testing metric for before and after we do the error correction with the tsukaba dataset

            # This function needs to be in the depth provider
            #self.depthProviderRef.updateDepthMap(percent)

            # Call toggleDraw() again once scaling is complete.
            self.pdRef.toggleDraw()
            #test.scaleFinish.signal.emit()
            #test.func()


        self.prevDist = self.dist


    def dot(self, o):
        return self.dx * o.dx + self.dy * o.dy + self.dz * o.dz

    def recalculate(self):
        self.dx = self.t.x - self.s.y
        self.dy = self.t.y - self.s.y
        self.dz = self.t.z - self.s.z

        dist = (self.dx ** 2 + self.dy ** 2 + self.dz ** 2) ** .5
        self.dist = dist

    def __str__(self):
        return f'{self.name}: <{self.dx:.1f}, {self.dy:.1f}, {self.dz:.1f}>'

    def serialize(self):
        return self.s.name, self.t.name
