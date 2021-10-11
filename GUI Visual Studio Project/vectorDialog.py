from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *

class vectorDialog(QDialog):
    def __init__(self,parent=None):
        # Initialize dialog window.
        super().__init__()
        self.setWindowTitle("Enter New Vector")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Drop-down menu.
        self.pointCombo = QComboBox(self)
        self.pointCombo2 = QComboBox(self)
        for i in range(parent.tableWidgetPoints.rowCount()):
            itemStr = parent.tableWidgetPoints.item(i,1).text() + "; " + parent.tableWidgetPoints.item(i,2).text()
            self.pointCombo.addItem(itemStr)
            self.pointCombo2.addItem(itemStr)

        # Create layout and add everything to it.
        self.layout = QFormLayout()
        message = QLabel("Enter information about the new point below.")
        self.layout.addRow(message)
        self.nameBox = QLineEdit(self)
        self.layout.addRow("Name:", self.nameBox)
        self.layout.addRow("Starting Point:", self.pointCombo)
        self.layout.addRow("Ending Point:", self.pointCombo2)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)

    # TODO: Decipher combo box choices to add vector to table.
    def addVector():
        vName = self.nameBox.text()

        #p1 = Point(self.nameBox.text())

