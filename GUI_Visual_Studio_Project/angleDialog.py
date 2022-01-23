from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
from angle import *
import numpy as np

class angleDialog(QDialog):
    # Initialize dialog window. 
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Enter New Angle")
        self.createLayout(pd)
        
    # Create form layout of dialog window.
    def createLayout(self, pd):
        self.message = QLabel("Enter information about the new angle below.")

        # Create button box.
        buttonOptions = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonOptions)
        self.buttonBox.accepted.connect(lambda: self.addAngle(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Create box for name input.
        self.nameBox = QLineEdit(self)

        # Create drop-down menus and fill them with available points.
        self.vectorCombo = QComboBox(self)
        self.vectorCombo2 = QComboBox(self)
        for vector in pd.vectors:
            itemStr = vector.getComboStr()
            self.vectorCombo.addItem(itemStr)
            self.vectorCombo2.addItem(itemStr)

        # Default indices are the last 2 points.
        if(pd.vectors.size >= 2):
            self.vectorCombo.setCurrentIndex(pd.vectors.size - 2)
            self.vectorCombo2.setCurrentIndex(pd.vectors.size - 1)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)  
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("First Vector:", self.vectorCombo)
        self.layout.addRow("Second Vector:", self.vectorCombo2)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # TODO: Check if angle already exists in table.
    def addAngle(self, pd):
        v1Index = self.vectorCombo.currentIndex()
        v2Index = self.vectorCombo2.currentIndex()

        aName = self.nameBox.text()
        angle = Angle(pd.vectors[v1Index], pd.vectors[v2Index], aName)

        if v1Index == v2Index:
            self.message.setText("You must enter two distinct vectors!")
        
        else:
            pd.angles = np.append(pd.angles, angle)
            pd.updateAngleTable()
            self.close()