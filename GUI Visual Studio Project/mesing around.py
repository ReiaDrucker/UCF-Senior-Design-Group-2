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


class ImageViewer(QtWidgets.QGraphicsView):
    factor = 2.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setBackgroundRole(QtGui.QPalette.Dark)

        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self._pixmap_item)

        self.lastItem = None

        

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            
            # Kind of works but the event happens on the widget need to translate to what the scene is showing
            x = self.mapToScene(event.pos()).x()
            y = self.mapToScene(event.pos()).y() 
            print(x)
            print(y)
            print()
            #
            #item = QGraphicsLineItem(x,y,x,y)
            #item.setPen(QPen(Qt.red, 4))
            item = QGraphicsRectItem(x-2,y-2,4,4)
            item.setPen(QPen(Qt.red, 1))
            item.setBrush(QBrush(Qt.red))
            self.lastItem = item
            self.scene.addItem(item)
        if event.button() == Qt.RightButton:
            try:
                self.scene.removeItem(self.lastItem)
            except:
                print()

    def load_image(self, fileName):
        pixmap = QtGui.QPixmap(fileName)
        if pixmap.isNull():
            return False
        self._pixmap_item.setPixmap(pixmap)
        return True

    def zoomIn(self):
        self.zoom(self.factor)
        
    def zoomOut(self):
        self.zoom(1 / self.factor)
    
    def zoom(self, f):
        self.scale(f, f)
        try:
            self.scene.removeItem(self.lastItem)
            self.scene.addItem(self.lastItem)
        except:
            print()

    def resetZoom(self):
        self.resetTransform()

    def fitToWindow(self):
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)


    ## MY STUFF



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.view = ImageViewer()
        self.setCentralWidget(self.view)

        self.createActions()
        self.createMenus()

        self.resize(960, 960)

    def open(self):
        image_formats = " ".join(
            [
                "*." + image_format.data().decode()
                for image_format in QtGui.QImageReader.supportedImageFormats()
            ]
        )
        

        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("Open Image"),
            QtCore.QDir.currentPath(),
            self.tr("Image Files({})".format(image_formats)),
        )
        if fileName:
            is_loaded = self.view.load_image(fileName)
            self.fitToWindowAct.setEnabled(is_loaded)
            self.updateActions()

    def fitToWindow(self):
        if self.fitToWindowAct.isChecked():
            self.view.fitToWindow()
        else:
            self.view.resetZoom()
        self.updateActions()

    def about(self):
        QtWidgets.QMessageBox.about(
            self,
            "ImageViewer",
            "ImageViewer",
        )

    def createActions(self):
        self.openAct = QtWidgets.QAction(
            "&Open...", self, shortcut="Ctrl+O", triggered=self.open
        )
        self.exitAct = QtWidgets.QAction(
            "E&xit", self, shortcut="Ctrl+Q", triggered=self.close
        )
        self.zoomInAct = QtWidgets.QAction(
            self.tr("Zoom &In (25%)"),
            self,
            shortcut="Ctrl+=",
            enabled=False,
            triggered=self.view.zoomIn,
        )
        self.zoomOutAct = QtWidgets.QAction(
            self.tr("Zoom &Out (25%)"),
            self,
            shortcut="Ctrl+-",
            enabled=False,
            triggered=self.view.zoomOut,
        )
        self.normalSizeAct = QtWidgets.QAction(
            self.tr("&Normal Size"),
            self,
            shortcut="Ctrl+S",
            enabled=False,
            triggered=self.view.resetZoom,
        )
        self.fitToWindowAct = QtWidgets.QAction(
            self.tr("&Fit to Window"),
            self,
            enabled=False,
            checkable=True,
            shortcut="Ctrl+F",
            triggered=self.fitToWindow,
        )

    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu(self.tr("&File"), self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtWidgets.QMenu(self.tr("&View"), self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
