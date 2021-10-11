import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

class PhotoDisplayer(QWidget):

    def __init__(self, width, height, parent=None):
        super(PhotoDisplayer, self).__init__(parent)
        self.window_width, self.window_height = width, height
        self.setMinimumSize(self.window_width, self.window_height)

        self.pix = QPixmap(self.rect().size())
        
        #Should be filled blue to start
        self.pix.fill(Qt.blue)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self.pix)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:            
            painter = QPainter(self.pix)
            painter.setPen(QPen(Qt.red, 5))
            painter.drawPoint(event.pos())
            x = event.pos().x()
            y = event.pos().y() 
            print(x)
            print(y)
            self.update()

    def setNewPixmap(self, new):
        self.pix = new
        self.update()
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PhotoDisplayer(960, 540)
    ex.show()
    sys.exit(app.exec_())
