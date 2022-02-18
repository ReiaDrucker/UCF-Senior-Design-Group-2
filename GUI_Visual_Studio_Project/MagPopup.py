from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MagPopup(QDialog):
    scaleFinish = pyqtSignal()

    def __init__(self):
        super().__init__()


        self.setWindowTitle("Recalculating...")

        self.message = QLabel("Re-scaling vector magnitudes, hold on...")
        self.layout = QVBoxLayout()

        message = QLabel("Re-scaling vector magnitudes, hold on...")

        self.layout.addWidget(message)

        self.setLayout(self.layout)

        #scaleFinish.signal.connect(self.func)
        # self.scaleFinish.signal.emit()

    def func(self):
        print("What")
        #self.close()
