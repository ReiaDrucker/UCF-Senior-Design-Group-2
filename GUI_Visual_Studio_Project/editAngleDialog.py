from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
from angle import *
import numpy as np

class editAngleDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Edit Angle")
        self.createLayout(pd)

    # Create form layout of dialog window.
    def createLayout(self, pd):
        self.message = QLabel("Select the angle to edit.")

        self.nameBox = QLineEdit(self)

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.editAngle(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.angleCombo = QComboBox(self)
        for angle in pd.angles:
            itemStr = angle.getComboStr()
            self.angleCombo.addItem(itemStr)
        self.angleCombo.currentIndexChanged.connect(lambda: self.fillBoxes(pd))

        # Create drop-down menus and fill them with available vectors.
        self.vectorCombo = QComboBox(self)
        self.vectorCombo2 = QComboBox(self)
        for vector in pd.vectors:
            itemStr = vector.getComboStr()
            self.vectorCombo.addItem(itemStr)
            self.vectorCombo2.addItem(itemStr)
        self.fillBoxes(pd)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)
        self.layout.addRow("Angle List:", self.angleCombo)
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Vector 1:", self.vectorCombo)
        self.layout.addRow("Vector 2:", self.vectorCombo2)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Fill in vector combo boxes based on point chosen.
    def fillBoxes(self, pd):
        curAngle = pd.angles[self.angleCombo.currentIndex()]
        v1Index = self.getVectorPos(pd.vectors, curAngle.vector1Ref)
        v2Index = self.getVectorPos(pd.vectors, curAngle.vector2Ref)
        self.nameBox.setText(curAngle.name)
        self.vectorCombo.setCurrentIndex(v1Index)
        self.vectorCombo2.setCurrentIndex(v2Index)

    # Adds new vector to table and lists through photoDisplayer.
    # TODO: Doesn't work yet.
    def editAngle(self, pd):
        # Get chosen index.
        v1Index = self.vectorCombo.currentIndex()
        v2Index = self.vectorCombo2.currentIndex()

        # If there are valid vectors.
        # Edit vector update table.
        #pd.vectors = np.delete(pd.vectors, vIndex)
        # Create new vector with points and name.
        aName = self.nameBox.text()
        ang = Angle(pd.vectors[v1Index], pd.vectors[v2Index], aName)

        # If same point selected twice, don't accept.
        if v1Index == v2Index:
            self.message.setText("You need to enter two distinct vectors!")

        # # If equivalent vector already exists, don't accept.
        # elif self.vectorExists(pd.vectors, vec):
        #     self.message.setText("Vector already exists!")

        # No errors, then accept.
        else:
            pd.angles[self.angleCombo.currentIndex()] = ang
            pd.updateAngleTable()
            #pd.update()
            self.close()

    # Get positions of point in points.
    def getVectorPos(self, vectors, vec):
        for i in range(len(vectors)):
            if vec.getPixelCoordinatesStr() == vectors[i].getPixelCoordinatesStr():
                return i
        return -1
