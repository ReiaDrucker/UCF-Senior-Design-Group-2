import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from point import *
from vector import *
from angle import *
import numpy as np
import os

class PhotoDisplayer(QWidget):

    def __init__(self, app, width = 1024, height = 1024):
        super().__init__()
        self.resize(width, height)

        self.app = app

        self.pix = QPixmap(width, height)
        self.pix.fill(Qt.blue)

        # Different pen styles for points and vectors
        self.pointPen = QPen(Qt.red, 5)
        self.vectorPen = QPen(Qt.black, 3)

        self.drawStuff = True

    def toggleDraw(self):
       self.drawStuff = not(self.drawStuff)
       self.update()

    def inBounds(self, xVal, yVal):
        return xVal >= 0 and yVal >= 0 and xVal <= self.width() and yVal <= self.height()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Paint the image to the screen
        painter.drawPixmap(QPoint(), self.pix)

        # Only draw the points and vectors if the toggle is set to true
        if(self.drawStuff):
            # Draw all the vectors
            self.drawVectors(painter)

            # Draw all the points
            self.drawPoints(painter)

    def addPoint(self, x, y):
        if(self.inBounds(x,y)):
            self.app.addPointAtPixel(x, y)

    def setNewPixmap(self, new):
        # When you get a new image resize the pixmap to fit it
        self.pix = new
        self.resize(self.pix.width(), self.pix.height())
        self.update()

    def drawVectors(self, painter):
        painter.setPen(self.vectorPen)

        #Draw all vectors
        for name, vec in self.app.vectorTable:
            # Access the points that made this vector and draw a line based on those coordinates
            painter.drawLine(vec.s.u, vec.s.v, vec.t.u, vec.t.v)

    def drawPoints(self, painter):
        painter.setPen(self.pointPen)
        painter.setBrush(painter.pen().color())

        # Draw all points
        for name, point in self.app.pointTable:
            # TODO: resize on selection?
            sz = 1
            painter.drawEllipse(QPointF(point.u, point.v), sz, sz)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PhotoDisplayer(960, 540)
    ex.show()
    sys.exit(app.exec_())
