from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class changeColorDialog(QDialog):
    # Pass 0 to change the vector color
    # Pass 1 to change the point color
    def __init__(self,parent=None,changeType=None):
        # Initialize dialog window.
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Select Color")
        self.changePoint = changeType;

        self.colors = [Qt.white, Qt.black, Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow]
        self.colorNames = ["White", "Black", "Red", "Green", "Blue", "Cyan", "Magenta", "Yellow"]

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.changeColor(self.parent, changeType))
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.colorCombo = QComboBox(self)

        for i in range(len(self.colors)):
            itemStr = self.colorNames[i]
            self.colorCombo.addItem(itemStr)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        self.message = QLabel("Select the color you would like.")
        self.layout.addRow(self.message)
        self.layout.addRow("Color Options:", self.colorCombo)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # Adds new vector to table and lists through photoDisplayer.
    def changeColor(self, parent, changeType):
        cIndex = self.colorCombo.currentIndex()
        if(self.changePoint == 1):
            parent.pd.pointPen = QPen(self.colors[cIndex], 5)
        if(self.changePoint == 0):
            parent.pd.vectorPen = QPen(self.colors[cIndex], 3)
        parent.pd.update()
        self.close()
