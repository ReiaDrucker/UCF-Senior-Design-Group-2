from PyQt5 import QtCore, QtGui, QtWidgets

class ColorSelector(QtWidgets.QComboBox):
    color_map = {
        'White': QtCore.Qt.white,
        'Black': QtCore.Qt.black,
        'Red': QtCore.Qt.red,
        'Green': QtCore.Qt.green,
        'Blue': QtCore.Qt.blue,
        'Cyan': QtCore.Qt.cyan,
        'Magenta': QtCore.Qt.magenta,
        'Yellow': QtCore.Qt.yellow,
    }

    def __init__(self, color = None):
        super().__init__()

        self.colors = []
        for k, v in self.color_map.items():
            self.addItem(k, userData=v)

        if color:
            cur_idx = self.findData(color)
            self.setCurrentIndex(cur_idx)

    def set_color(self, color):
        cur_idx = self.findData(color)
        self.setCurrentIndex(cur_idx)

    def get_color(self):
        return QtCore.Qt.GlobalColor(self.currentData())
