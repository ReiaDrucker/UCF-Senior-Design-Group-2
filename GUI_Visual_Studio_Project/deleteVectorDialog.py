from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
import numpy as np

class deleteVectorDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Delete Vector")
        self.createLayout(pd)
        
    # Create form layout of dialog window. 
    def createLayout(self, pd):
        self.message = QLabel("Select the vector to delete.")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.deleteVector(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.vectorCombo = QComboBox(self)
        for vector in pd.vectors:
            itemStr = vector.getComboStr()
            self.vectorCombo.addItem(itemStr)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.layout.addRow(self.message)
        self.layout.addRow("Vector List:", self.vectorCombo)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    def deleteVector(self, pd):
        # Get chosen index.
        vIndex = self.vectorCombo.currentIndex()
        
        # If there are valid vectors.
        #if vIndex >= 0:
        # Remove vector from list and update table.
        pd.vectors = np.delete(pd.vectors, vIndex)
        pd.updateVectorTable()
        pd.update()
            
        self.close()