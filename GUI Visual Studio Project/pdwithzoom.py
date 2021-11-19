import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from point import *
from vector import *
import numpy as np
import os

class ZoomyPhotoDisplayer(QGraphicsView):
    factor = 2.0

    def __init__(self, width, height, pTable=None, vTable=None, parent=None):
        super(ZoomyPhotoDisplayer, self).__init__(parent)
        self.setMaximumWidth(width)
        self.setMaximumHeight(height)
        self.resize(width, height)

        self.pTable = pTable
        self.vTable = vTable

        # Different pen styles for points and vectors
        self.pointPen = QPen(Qt.red, 1)
        self.vectorPen = QPen(Qt.black, 3)

        # Initialize point/vector arrays for tables.
        self.points = np.array([])
        self.vectors = np.array([])

        self.drawStuff = False

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setBackgroundRole(QPalette.Dark)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self._pixmap_item)

    def zoomIn(self):
        self.zoom(self.factor)
        
    def zoomOut(self):
        self.zoom(1 / self.factor)
    
    def zoom(self, f):
        self.scale(f, f)

    def resetZoom(self):
        self.resetTransform()

    def toggleDraw(self):
       self.drawStuff = not(self.drawStuff)
       #self.update()

    def inBounds(self, xVal, yVal):
        return xVal >= 0 and yVal >= 0 and xVal <= self.width() and yVal <= self.height()

    def mousePressEvent(self, event):
        if(self.drawStuff):
            if event.button() == Qt.LeftButton:            
                x = self.mapToScene(event.pos()).x()
                y = self.mapToScene(event.pos()).y() 

                # Determine name of new point.
                newPoint = Point(self.getAutoName(), 0, 0, 0, x, y)
            
                # Add point to array.
                self.points = np.append(self.points, newPoint)

                # Update table with new point.
                self.updatePointTable()

    # Get autogenerated name based on alphabet.
    def getAutoName(self):
        if (self.points.size > 25):
            case = ord('a')
        else:
            case = ord('A')
        return chr(self.points.size % 26 + case)


    def setNewPixmap(self, new):
        self.drawStuff = True
        self.resize(new.width(), new.height())
        self._pixmap_item.setPixmap(new)

    # This should get called anytime something changes rn it only does that when we update the point table which is not ideal
    # Ideally I'd like to override the paint or update event and just add these lines after calling super().update() or something
    def renderStuff(self):
        
        # Clear the points of the items lists so we don't get duplicates
        for item in self.scene.items():
            if(type(item) == QGraphicsLineItem or type(item) == QGraphicsRectItem):
                self.scene.removeItem(item)

        # Draw the new ones
        if self.drawStuff:
            self.drawPoints()
            self.drawVectors()
        self.update()
        #print("updating")
        #super().update()

    def drawVectors(self):

        #Draw all vectors
        for vec in self.vectors:
            # Access the points that made this vector and draw a line based on those coordinates
            item = QGraphicsLineItem(vec.getReferencePoints()[0].getPixelCoordinates()[0],vec.getReferencePoints()[0].getPixelCoordinates()[1],
                                     vec.getReferencePoints()[1].getPixelCoordinates()[0], vec.getReferencePoints()[1].getPixelCoordinates()[1])
            item.setPen(self.vectorPen)
            self.scene.addItem(item)
    
    def drawPoints(self):
        # Draw all points
        for point in self.points:
            pointSize = 4
            item = QGraphicsRectItem(point.getPixelCoordinates()[0]-pointSize/2,point.getPixelCoordinates()[1]-pointSize/2,pointSize,pointSize)
            item.setPen(self.pointPen)
            item.setBrush(QBrush(self.pointPen.color()))
            self.scene.addItem(item)
        
    # Update point table with new point in array.
    def updatePointTable(self):
        if self.pTable != None:
            self.pTable.clearContents()
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
            if (self.drawStuff):
                self.renderStuff()
                
        

    # Update vector table with new vector in array.
    def updateVectorTable(self):
        if self.vTable != None:
            self.vTable.clearContents()
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
                item = QTableWidgetItem("{:.3f}".format(np.linalg.norm(curVector.getPixelCoordinates())))
                item.setTextAlignment(Qt.AlignCenter)
                self.vTable.setItem(count, 3, item)
            if (self.drawStuff):
                self.renderStuff()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ZoomyPhotoDisplayer(960, 540)
    ex.show()
    sys.exit(app.exec_())
