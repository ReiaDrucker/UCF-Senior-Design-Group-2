from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
from angle import *
import numpy as np

class deleteAngleDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Delete Angle")
        self.createLayout(pd)
        
    # Create form layout of dialog window. 
    def createLayout(self, pd):
        self.message = QLabel("Select the angle to delete.")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.deleteAngle(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.angleCombo = QComboBox(self)
        for angle in pd.angles:
            itemStr = angle.getComboStr()
            self.angleCombo.addItem(itemStr)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)
        self.layout.addRow("Angle List:", self.angleCombo)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    def deleteAngle(self, pd):
        # Get chosen index.
        aIndex = self.angleCombo.currentIndex()
        
        # If there are valid vectors.
        #if vIndex >= 0:
        # Remove vector from list and update table.
        pd.angles = np.delete(pd.angles, aIndex)
        pd.updateAngleTable()
        pd.update()
            
        self.close()