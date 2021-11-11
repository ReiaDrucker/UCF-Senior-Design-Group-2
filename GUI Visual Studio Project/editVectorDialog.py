from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class editVectorDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Edit Vector")
        self.createLayout(pd)
        
    # Create form layout of dialog window. 
    def createLayout(self, pd):
        self.message = QLabel("Select the vector to edit.")

        self.nameBox = QLineEdit(self)

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.editVector(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.vectorCombo = QComboBox(self)
        for vector in pd.vectors:
            itemStr = vector.getComboStr()
            self.vectorCombo.addItem(itemStr)
        self.vectorCombo.currentIndexChanged.connect(lambda: self.fillBoxes(pd))

        # Create drop-down menus and fill them with available points.
        self.pointCombo = QComboBox(self)
        self.pointCombo2 = QComboBox(self)
        for point in pd.points:
            itemStr = point.getComboStr()
            self.pointCombo.addItem(itemStr)
            self.pointCombo2.addItem(itemStr)
        self.fillBoxes(pd)        

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)
        self.layout.addRow("Vector List:", self.vectorCombo)
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Point 1:", self.pointCombo)
        self.layout.addRow("Point 2:", self.pointCombo2)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Fill in point combo boxes based on selected
    def fillBoxes(self, pd):
        curVector = pd.vectors[self.vectorCombo.currentIndex()]
        p1Index = self.getPointPos(pd.points, curVector.getReferencePoints()[0])
        p2Index = self.getPointPos(pd.points, curVector.getReferencePoints()[1])
        self.nameBox.setText(curVector.name)
        self.pointCombo.setCurrentIndex(p1Index)
        self.pointCombo2.setCurrentIndex(p2Index)

    # Adds new vector to table and lists through photoDisplayer.
    def editVector(self, pd):
        # Get chosen index.
        p1Index = self.pointCombo.currentIndex()
        p2Index = self.pointCombo2.currentIndex()
        
        # If there are valid vectors.
        # Edit vector update table.
        #pd.vectors = np.delete(pd.vectors, vIndex)
        # Create new vector with points and name.
        vName = self.nameBox.text()     
        vec = Vector(pd.points[p1Index], pd.points[p2Index], vName)

        # If same point selected twice, don't accept.            
        if p1Index == p2Index:
            self.message.setText("You need to enter two distinct points!")

        # If equivalent vector already exists, don't accept.
        elif self.vectorExists(pd.vectors, vec):
            self.message.setText("Vector already exists!")

        # No errors, then accept.
        else:
            pd.vectors[self.vectorCombo.currentIndex()] = vec
            pd.updateVectorTable()
            pd.update()
            self.close()
    
    # Get positions of point in points.
    def getPointPos(self, points, point):
        for i in range(len(points)):
            if point.getPixelCoordinatesStr() == points[i].getPixelCoordinatesStr():
                return i
        return -1

    # Checks if vector exists in pd's vector list.
    def vectorExists(self, vectors, vec):
        for v in vectors:
            if v.getPixelCoordinatesStr() == vec.getPixelCoordinatesStr():
                return True
        return False