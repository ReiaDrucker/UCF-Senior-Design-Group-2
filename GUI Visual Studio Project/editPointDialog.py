from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class editPointDialog(QDialog):
    def __init__(self,parent=None):
        # Initialize dialog window.
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Edit Vector")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.editPoint(parent))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.pointCombo = QComboBox(self)
        for i in range(parent.pointTable.rowCount()):
            itemStr = parent.pointTable.item(i,0).text() + ": " + parent.pointTable.item(i,1).text() + "; " + parent.pointTable.item(i,2).text()
            self.pointCombo.addItem(itemStr)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.message = QLabel("Select the point to delete.")
        self.layout.addRow(self.message)
        self.layout.addRow("Point List:", self.pointCombo)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    def editPoint(self, parent):
        pIndex = self.pointCombo.currentIndex()

        if pIndex >= 0:
            parent.pd.points = np.delete(parent.pd.points, pIndex)
            parent.pointTable.removeRow(pIndex)
            parent.pd.update()

        self.close()