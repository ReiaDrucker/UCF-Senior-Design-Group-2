from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class deleteVectorDialog(QDialog):
    def __init__(self,parent=None):
        # Initialize dialog window.
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Delete Vector")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.deleteVector(parent))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.vectorCombo = QComboBox(self)
        for v in parent.pd.vectors:
            itemStr = v.name + ": " + v.getPixelCoordinatesStr() + "; " + v.getRealCoordinatesStr()
            self.vectorCombo.addItem(itemStr)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.message = QLabel("Select the vector to delete.")
        self.layout.addRow(self.message)
        self.layout.addRow("Vector List:", self.vectorCombo)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    def deleteVector(self, parent):
        vIndex = self.vectorCombo.currentIndex()
        
        if vIndex >= 0:
            parent.pd.vectors = np.delete(parent.pd.vectors, vIndex)
            parent.vectorTable.removeRow(vIndex)
            parent.pd.update()
        self.close()