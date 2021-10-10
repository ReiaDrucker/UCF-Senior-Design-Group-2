from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class pointDialog(QDialog):
    def __init__(self,parent=None):
        # Initialize dialog window.
        super().__init__()
        self.setWindowTitle("Enter New Point")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # First mesage.
        message = QLabel("Enter information about the new point below.")

        # Text input boxes.
        self.nameBox = QLineEdit(self)
        self.pixelBox = QLineEdit(self)
        self.realBox = QLineEdit(self)
        

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        #self.layout.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addRow(message)
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Pixel Coordinates:", self.pixelBox)
        self.layout.addRow("Real Coordinates:", self.realBox)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)
