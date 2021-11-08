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
        self.setMaximumWidth(width)
        self.setMaximumHeight(height)
        self.resize(width, height)

        self.pix = QPixmap(self.rect().size())
        
        #Should be filled blue to start
        self.pix.fill(Qt.blue)

        self.pTable = pTable
        self.vTable = vTable

        # Different pen styles for points and vectors
        self.pointPen = QPen(Qt.red, 5)
        self.vectorPen = QPen(Qt.black, 3)

        # Initialize point/vector arrays for tables.
        self.points = np.array([])
        self.vectors = np.array([])

        self.drawStuff = True

    def toggleDraw(self):
       self.drawStuff = not(self.drawStuff)
       print(self.drawStuff)
       self.update()


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

    def mousePressEvent(self, event):
        if(self.drawStuff):
            if event.button() == Qt.LeftButton:            
                x = event.pos().x()
                y = event.pos().y() 

                # Determine name of new point.
                if (self.points.size > 25):
                    case = ord('a')
                else:
                    case = ord('A')
                pName = chr(self.points.size % 26 + case)
            
                # Add point to array.
                self.points = np.append(self.points, Point(pName, 0, 0, 0, x, y))
            
            # For now make a vector with the two most recent points when we draw a point
            # if(self.points.size >= 2):
            #     v = Vector(self.points[len(self.points) - 2], self.points[len(self.points) - 1])
            #     #self.vectors = np.append(self.vectors, Vector(self.points[len(self.points) - 2], self.points[len(self.points) - 1]))
            #     self.updateVectorTable(v)

                # Update table with new point.
                self.updatePointTable()

                self.update()

    def setNewPixmap(self, new):

        # When you get a new image resize the pixmap to fit it
        self.pix = new
        self.resize(self.pix.width(), self.pix.height())
        self.update()

    def drawVectors(self, painter):
        painter.setPen(self.vectorPen)

        #Draw all vectors
        for vec in self.vectors:
            # Access the points that made this vector and draw a line based on those coordinates
            painter.drawLine(vec.getReferencePoints()[0].getPixelCoordinates()[0], vec.getReferencePoints()[0].getPixelCoordinates()[1],
                                vec.getReferencePoints()[1].getPixelCoordinates()[0], vec.getReferencePoints()[1].getPixelCoordinates()[1])
    
    def drawPoints(self, painter):
        painter.setPen(self.pointPen)

        # Draw all points
        for point in self.points:
            painter.drawPoint(point.getPixelCoordinates()[0], point.getPixelCoordinates()[1])
        
    # Update point table with new point in array.
    def updatePointTable(self):
        if self.pTable != None:
            self.pTable.clear()
            self.pTable.setRowCount(0)

            for count in range(self.points.size):
                # Create new row and give it proper header name.
                curPoint = self.points[count]
                self.pTable.insertRow(count)

                item = QTableWidgetItem("Point " + str(count + 1))
                item.setTextAlignment(Qt.AlignCenter)
                self.pTable.setVerticalHeaderItem(count, item)

                # Set name column.
                item = QTableWidgetItem(curPoint.name)
                item.setTextAlignment(Qt.AlignCenter)
                self.pTable.setItem(count, 0, item)

                # Set pixel coordinates column.
                item = QTableWidgetItem(curPoint.getPixelCoordinatesStr())
                item.setTextAlignment(Qt.AlignCenter)
                self.pTable.setItem(count, 1, item)

                # Set real coordinates column.
                item = QTableWidgetItem(curPoint.getRealCoordinatesStr())
                item.setTextAlignment(Qt.AlignCenter)
                self.pTable.setItem(count, 2, item)

    # Update vector table with new vector in array.
    def updateVectorTable(self):
        if self.vTable != None:
            self.vTable.clear()
            self.vTable.setRowCount(0)
            for count in range(self.vectors.size):
                # Create new row and give it proper header name.
                #self.vectors = np.append(self.vectors, curVector)
                #count = self.vectors.size - 1
                curVector = self.vectors[count]

                #curVector = self.vectors[count]
                self.vTable.insertRow(count)

                item = QTableWidgetItem("Vector " + str(count + 1))
                item.setTextAlignment(Qt.AlignCenter)
                self.vTable.setVerticalHeaderItem(count, item)

                # Set name column.
                item = QTableWidgetItem(curVector.name)
                item.setTextAlignment(Qt.AlignCenter)
                self.vTable.setItem(count, 0, item)

                # Set pixel coordinates column.
                item = QTableWidgetItem(curVector.getPixelCoordinatesStr())
                item.setTextAlignment(Qt.AlignCenter)
                self.vTable.setItem(count, 1, item)

                # Set real coordinates column.
                item = QTableWidgetItem(curVector.getRealCoordinatesStr())
                item.setTextAlignment(Qt.AlignCenter)
                self.vTable.setItem(count, 2, item)

                # Set magnitude column.
                item = QTableWidgetItem(str(np.linalg.norm(curVector.getPixelCoordinates())))
                item.setTextAlignment(Qt.AlignCenter)
                self.vTable.setItem(count, 3, item)

   

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PhotoDisplayer(960, 540)
    ex.show()
    sys.exit(app.exec_())
