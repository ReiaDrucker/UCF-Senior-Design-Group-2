from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class parameterDialog(QDialog):
    # Initialize dialog window.
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Confirm Parameters")
        self.createLayout(pd)

    # Create form layout of dialog window.
    def createLayout(self, pd):
        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        #self.buttonBox.accepted.connect(lambda: self.tuneParameters(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Other stuff here.
        self.text1 = QLineEdit()
        self.text2 = QLineEdit()
                
        self.layout = QFormLayout()
        self.layout.addRow("Box 1:", self.text1)
        self.layout.addRow("Box 2:", self.text2)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    # Edits parameters.
    def editParameters(self, pd):
        print("Filler")

if __name__ == "__main__":
    dialog = editParametersDialog(None)
    dialog.exec()