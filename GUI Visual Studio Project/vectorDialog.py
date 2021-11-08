from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class vectorDialog(QDialog):
    def __init__(self,parent=None):
        # Initialize dialog window.
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Enter New Vector")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(self.addVector)
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.pointCombo = QComboBox(self)
        self.pointCombo2 = QComboBox(self)
        for i in range(parent.pointTable.rowCount()):
            itemStr = parent.pointTable.item(i,0).text() + ": " + parent.pointTable.item(i,1).text() + "; " + parent.pointTable.item(i,2).text()
            self.pointCombo.addItem(itemStr)
            self.pointCombo2.addItem(itemStr)

        # Default indices are the last 2 points
        if(parent.pointTable.rowCount() >= 2):
            self.pointCombo.setCurrentIndex(parent.pointTable.rowCount()-2)
            self.pointCombo2.setCurrentIndex(parent.pointTable.rowCount()-1)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.message = QLabel("Enter information about the new point below.")
        self.layout.addRow(self.message)
        self.nameBox = QLineEdit(self)
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Starting Point:", self.pointCombo)
        self.layout.addRow("Ending Point:", self.pointCombo2)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    def addVector(self):
        vName = self.nameBox.text()
        p1Index = self.pointCombo.currentIndex()
        p2Index = self.pointCombo2.currentIndex()

        if p1Index >= 0 and p2Index >= 0:
            # If textbox for name is empty, give default name.
            if vName == "":
                vName = self.parent.pd.points[p1Index].name + "-" + self.parent.pd.points[p2Index].name

            # Create new vector.
            v = Vector(self.parent.pd.points[p1Index], self.parent.pd.points[p2Index])
            v.name = vName

            # If same point selected twice, don't accept.
            
            if p1Index == p2Index:
                self.message.setText("You need to enter two distinct points!")
            else:
                # If equivalent vector already exists, don't accept.
                exists = False
                for vec in self.parent.pd.vectors:
                    if v.getPixelCoordinatesStr() == vec.getPixelCoordinatesStr():
                        exists = True
                if exists == True:
                    self.message.setText("Vector already exists!")
                # No errors, then accept.
                else:
                    self.parent.pd.vectors = np.append(self.parent.pd.vectors, v)
                    self.parent.pd.updateVectorTable()
                    self.parent.pd.update()
                    self.close()
        else:
            self.close()