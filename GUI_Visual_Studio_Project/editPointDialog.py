from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class editPointDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        # Initialize dialog window.
        super().__init__()
        self.setWindowTitle("Edit Point")
        self.createLayout(pd)

    # Create form layout for dialog window.
    def createLayout(self, pd):
        self.message = QLabel("Select the point to edit.")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.editPoint(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.pointCombo = QComboBox(self)
        for point in pd.points:
            itemStr = point.getComboStr()
            self.pointCombo.addItem(itemStr)
        self.pointCombo.currentIndexChanged.connect(lambda: self.fillBoxes(pd))

        # Text input boxes.
        self.nameBox = QLineEdit(self)
        self.pixelXBox = QLineEdit(self)
        self.pixelYBox = QLineEdit(self)
        self.realXBox = QLineEdit(self)
        self.realYBox = QLineEdit(self)
        self.realZBox = QLineEdit(self)
        self.fillBoxes(pd)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)
        self.layout.addRow("Point List:", self.pointCombo)
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Pixel X:", self.pixelXBox)
        self.layout.addRow("Pixel Y:", self.pixelYBox)
        self.layout.addRow("Real X:", self.realXBox)
        self.layout.addRow("Real Y:", self.realYBox)
        self.layout.addRow("Real Z:", self.realZBox)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Fills in textbox contents based on current point choice.
    def fillBoxes(self, pd):
        curPoint = pd.points[self.pointCombo.currentIndex()]
        self.nameBox.setText(curPoint.name)
        self.pixelXBox.setText(str(curPoint.pixelCoordinates[0]))
        self.pixelYBox.setText(str(curPoint.pixelCoordinates[1]))
        self.realXBox.setText(str(curPoint.realCoordinates[0]))
        self.realYBox.setText(str(curPoint.realCoordinates[1]))
        self.realZBox.setText(str(curPoint.realCoordinates[2]))

    # Adds new vector to table and lists through photoDisplayer.
    # TODO: If vector uses now-edited point, edit that vector.
    def editPoint(self, pd):
        # Get name or autogenerate it.
        pName = self.nameBox.text()
        if pName == "":
            pName = pd.getAutoName()

        # TODO: Checks on whether input is valid.

        # Convert text input into ints.
        realX = int(self.realXBox.text())
        realY = int(self.realYBox.text())
        realZ = int(self.realZBox.text())
        pixelX = int(self.pixelXBox.text())
        pixelY = int(self.pixelYBox.text())

        # Create new point and add to list and table.
        p = Point(pName, realX, realY, realZ, pixelX, pixelY)
        pd.points[self.pointCombo.currentIndex()] = p
        pd.updatePointTable()
        pd.update()

        self.close()