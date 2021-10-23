import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from point import *
from vector import *
import numpy as np
import os

class PhotoDisplayer(QWidget):

    def __init__(self, width, height, pTable=None, vTable=None, parent=None):
        super(PhotoDisplayer, self).__init__(parent)
        self.window_width, self.window_height = width, height
        self.setMinimumSize(self.window_width, self.window_height)

        self.pix = QPixmap(self.rect().size())
        
        #Should be filled blue to start
        self.pix.fill(Qt.blue)

        self.testPoint1 = None
        self.testPoint2 = None

        self.pTable = pTable
        self.vTable = vTable

        # Different pen styles for points and vectors
        self.pointPen = QPen(Qt.red, 5)
        self.vectorPen = QPen(Qt.black, 3)

        # Initialize point/vector arrays for tables.
        self.points = np.array([])
        self.vectors = np.array([])


    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawPixmap(QPoint(), self.pix)
        
        # This is how we draw a vector between two points
        self.drawVector(self.testPoint1, self.testPoint2, painter)

        painter.setPen(self.pointPen)

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
                self.testPoint1 = Point("Point " + str(self.points.size + 1), 0, 0, 0, x, y)
                self.points = np.append(self.points, self.testPoint1)
            else:
                self.testPoint2 = Point("Point " + str(self.points.size + 1), 0, 0, 0, x, y)
                self.points = np.append(self.points, self.testPoint2)
                self.vectors = np.append(self.vectors, Vector(self.testPoint1, self.testPoint2))
                self.updateVectorTable()

            self.updatePointTable()
            self.update()

    def setNewPixmap(self, new):
        self.pix = new
        self.update()

    def drawVector(self, p1, p2, painter):
        if(p1 != None and p2 != None):
            painter.setPen(self.vectorPen)
            painter.drawLine(p1.getPixelCoordinates()[0],p1.getPixelCoordinates()[1],p2.getPixelCoordinates()[0],p2.getPixelCoordinates()[1])

    # Update point table with new point in array.
    def updatePointTable(self):
        if self.pTable != None:
            # Create new row and give it proper header name.
            count = self.points.size - 1
            curPoint = self.points[count]
            self.pTable.insertRow(count)

            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            item.setText("Point " + str(count + 1))
            self.pTable.setVerticalHeaderItem(count, item)

            # Set name column.
            item = QTableWidgetItem()
            print(curPoint.name)
            item.setTextAlignment(Qt.AlignCenter)
            item.setText(curPoint.name)
            self.pTable.setItem(count, 0, item)

            # Set pixel coordinates column.
            item = QTableWidgetItem()
            item.setText(curPoint.getPixelCoordinatesStr())
            item.setTextAlignment(Qt.AlignCenter)
            self.pTable.setItem(count, 1, item)

            # Set real coordinates column.
            item = QTableWidgetItem()
            item.setText(curPoint.getRealCoordinatesStr())
            item.setTextAlignment(Qt.AlignCenter)
            self.pTable.setItem(count, 2, item)

    # Update vector table with new vector in array.
    def updateVectorTable(self):
        if self.vTable != None:
            # Create new row and give it proper header name.
            count = self.vectors.size - 1
            curVector = self.vectors[count]
            self.vTable.insertRow(count)

            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            item.setText("Vector " + str(count + 1))
            self.vTable.setVerticalHeaderItem(count, item)

            # Set name column.
            item = QTableWidgetItem()
            print(curVector.name)
            item.setTextAlignment(Qt.AlignCenter)
            item.setText(curVector.name)
            self.vTable.setItem(count, 0, item)

            # Set pixel coordinates column.
            item = QTableWidgetItem()
            item.setText(curVector.getPixelCoordinatesStr())
            item.setTextAlignment(Qt.AlignCenter)
            self.vTable.setItem(count, 1, item)

            # Set real coordinates column.
            item = QTableWidgetItem()
            item.setText(curVector.getRealCoordinatesStr())
            item.setTextAlignment(Qt.AlignCenter)
            self.vTable.setItem(count, 2, item)

            # TODO: Magnitude, should be easy but it's not a function in the vector class yet
            # so I'm leaving it blank for now.

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PhotoDisplayer(960, 540)
    ex.show()
    sys.exit(app.exec_())
