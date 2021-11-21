from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class vectorDialog(QDialog):
    # Initialize dialog window. 
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Enter New Vector")
        self.createLayout(pd)
        
    # Create form layout of dialog window.
    def createLayout(self, pd):
        self.message = QLabel("Enter information about the new vector below.")

        # Create button box.
        buttonOptions = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonOptions)
        self.buttonBox.accepted.connect(lambda: self.addVector(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Create box for name input.
        self.nameBox = QLineEdit(self)

        # Create drop-down menus and fill them with available points.
        self.pointCombo = QComboBox(self)
        self.pointCombo2 = QComboBox(self)
        for point in pd.points:
            itemStr = point.getComboStr()
            self.pointCombo.addItem(itemStr)
            self.pointCombo2.addItem(itemStr)

        # Default indices are the last 2 points.
        if(pd.points.size >= 2):
            self.pointCombo.setCurrentIndex(pd.points.size - 2)
            self.pointCombo2.setCurrentIndex(pd.points.size - 1)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)  
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Starting Point:", self.pointCombo)
        self.layout.addRow("Ending Point:", self.pointCombo2)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    def addVector(self, pd):
        # Get chosen indexes of combo boxes.
        p1Index = self.pointCombo.currentIndex()
        p2Index = self.pointCombo2.currentIndex()

        # If both indexes are valid, i.e. there are actually points.
        if p1Index >= 0 and p2Index >= 0:
            # Create new vector with points and name.
            vName = self.nameBox.text()     
            vec = Vector(pd.points[p1Index], pd.points[p2Index], vName)

            # If same point selected twice, don't accept.            
            if p1Index == p2Index:
                self.message.setText("You need to enter two distinct points!")

            elif pd.drawStuff == False:
                self.message.setText("You cannot add a vector when display is turned off!")

            # If equivalent vector already exists, don't accept.
            elif vectorDialog.vectorExists(pd.vectors, vec):
                self.message.setText("Vector already exists!")

            # No errors, then accept.
            else:
                pd.vectors = np.append(pd.vectors, vec)
                pd.updateVectorTable()
                pd.update()
                self.close()

        # If no valid points to choose, just close on attempted accept.
        else:
            self.close()

    # Checks if vector exists in pd's vector list.
    def vectorExists(vectors, vec):
        for v in vectors:
            if v.getPixelCoordinatesStr() == vec.getPixelCoordinatesStr():
                return True
        return False