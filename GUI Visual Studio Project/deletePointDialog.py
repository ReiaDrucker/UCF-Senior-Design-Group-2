from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class deletePointDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        # Initialize dialog window.
        super().__init__()
        self.setWindowTitle("Delete Point")
        self.createLayout(pd)

    # Create form layout for dialog window.
    def createLayout(self, pd):
        self.message = QLabel("Select the point to delete.")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.deletePoint(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.pointCombo = QComboBox(self)
        for point in pd.points:
            itemStr = point.getComboStr()
            self.pointCombo.addItem(itemStr)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)
        self.layout.addRow("Point List:", self.pointCombo)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    # TODO: If vector uses now-deleted point, delete that vector from vector list too.
    def deletePoint(self, pd):
        # Get chosen index.
        pIndex = self.pointCombo.currentIndex()

        # If there are valid points.
        #if pIndex >= 0:
        pd.points = np.delete(pd.points, pIndex)
        pd.updatePointTable()
        pd.update()

        self.close()