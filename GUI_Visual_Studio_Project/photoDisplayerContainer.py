from PyQt5 import QtWidgets, QtGui, QtCore
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from point import *
from vector import *
from photoDisplayer import *
import numpy as np
import os

class photoDisplayerContainer(QtWidgets.QGraphicsView):
    factor = 2.0

    def __init__(self, parent=None, pd=None):
        super().__init__(parent)

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setBackgroundRole(QtGui.QPalette.Dark)

        self.scene = QtWidgets.QGraphicsScene()

        self.setScene(self.scene)
        self.pd = pd
        self.scene.addWidget(self.pd)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = self.mapToScene(event.pos()).x()
            y = self.mapToScene(event.pos()).y()
            self.pd.addPoint(x, y)

    def zoomIn(self):
        self.zoom(self.factor)

    def zoomOut(self):
        self.zoom(1 / self.factor)

    def zoom(self, f):
        self.scale(f, f)

    def resetZoom(self):
        self.resetTransform()

    def fitToWindow(self):
        self.setSceneRect(QRectF(self.pd.rect()))
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)
