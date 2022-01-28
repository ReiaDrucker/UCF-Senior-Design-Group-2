from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from vector import *
from point import *
from angle import *
import numpy as np

class editParametersDialog:
    # Initialize dialog window.
    def __init__(self, pd):
        super().__init__()
        self.setWindowTitle("Tune Hyperparameters")
        self.createLayout(pd)

    # Create form layout of dialog window.
    def createLayout(self, pd):
        self.message = QLabel("Hyperparameter Tuning")

        # Create button box.
        buttonBox = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttonBox)
        self.buttonBox.accepted.connect(lambda: self.tuneParameters(pd))
        self.buttonBox.rejected.connect(self.reject)

        # Other stuff here.

        self.layout = QFormLayout()
        self.layout.addRow(self.message)
        self.layout.addRow(self.buttonBox)
        self.setLayout(self.layout)


    def tuneParameters(self, pd):
        print("Placeholder")
