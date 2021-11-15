from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from point import *
import numpy as np

class pointDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        # Initialize dialog window.
        super().__init__()
        self.setWindowTitle("Enter New Point")
        self.createLayout(pd)
        
    # Creates form layout of dialog window.
    def createLayout(self, pd):
        # Create button box.    
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.addPoint(pd))
        self.buttonBox.rejected.connect(self.reject)

        # First mesage.
        message = QLabel("Enter information about the new point below.")

        # Text input boxes.
        self.nameBox = QLineEdit(self)
        self.pixelXBox = QLineEdit(self)
        self.pixelYBox = QLineEdit(self)

        # TODO: Something else with real coordinates, but just 0 for now.
        self.realXBox = QLineEdit("0", self)
        self.realYBox = QLineEdit("0", self)
        self.realZBox = QLineEdit("0", self)
        
        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(message)
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Pixel X:", self.pixelXBox)
        self.layout.addRow("Pixel Y:", self.pixelYBox)
        self.layout.addRow("Real X:", self.realXBox)
        self.layout.addRow("Real Y:", self.realYBox)
        self.layout.addRow("Real Z:", self.realZBox)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new point to table and list through photoDisplayer.
    def addPoint(self, pd):
        # Get name or autogenerate it.
        pName = self.nameBox.text()
        if pName == "":
            pName = pd.getAutoName()

        # TODO: Checks on whether input is valid.
        try:
            # Convert text input into ints.
            realX = int(self.realXBox.text())
            realY = int(self.realYBox.text())
            realZ = int(self.realZBox.text())
            pixelX = int(self.pixelXBox.text())
            pixelY = int(self.pixelYBox.text())
            # Create new point and add to list and table.
            #if(pd.inBounds(pixelX, pixelY) == True):
            p = Point(pName, realX, realY, realZ, pixelX, pixelY)
            pd.points = np.append(pd.points, p)
            pd.updatePointTable()
            pd.update()

            self.close()
        except:
            #message.setText("Please fill fields with integers only")
            self.update()

        
        #else:
            #print("not in bounds")
           # message.setText("Point is out of Bounds!")
           # self.update()