import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from point import *
from vector import *
import numpy as np
import os

class PhotoDisplayer(QWidget):

    def __init__(self, width, height, parent=None):
        super(PhotoDisplayer, self).__init__(parent)
        self.window_width, self.window_height = width, height
        self.setMinimumSize(self.window_width, self.window_height)

        self.pix = QPixmap(self.rect().size())
        
        #Should be filled blue to start
        self.pix.fill(Qt.blue)

        self.testPoint1 = None
        self.testPoint2 = None

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawPixmap(QPoint(), self.pix)
        

        # This is how we draw a vector between two points
        self.drawVector(self.testPoint1, self.testPoint2, painter)

        painter.setPen(QPen(Qt.red, 5))
        # If we have some points try to draw them
        if(self.testPoint1 != None):
            painter.drawPoint(self.testPoint1.getPixelCoordinates()[0],self.testPoint1.getPixelCoordinates()[1])
        if(self.testPoint2 != None):
            painter.drawPoint(self.testPoint2.getPixelCoordinates()[0],self.testPoint2.getPixelCoordinates()[1])

       

        #painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:            
            x = event.pos().x()
            y = event.pos().y() 
            print(event.pos())

            # Add these to a list should be what we actually do but for now it just sets point one and from then on updates point 2
            if(self.testPoint1 == None):
                self.testPoint1 = Point("Point 1", 0, 0, 0, x, y)
            else:
                self.testPoint2 = Point("Point 2", 0, 0, 0, x, y)
            
            self.update()

    def setNewPixmap(self, new):
        self.pix = new
        self.update()

    def drawVector(self, p1, p2, painter):
        if(p1 != None and p2 != None):
            painter.setPen(QPen(Qt.black, 3))
            painter.drawLine(p1.getPixelCoordinates()[0],p1.getPixelCoordinates()[1],p2.getPixelCoordinates()[0],p2.getPixelCoordinates()[1])
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PhotoDisplayer(960, 540)
    ex.show()
    sys.exit(app.exec_())
