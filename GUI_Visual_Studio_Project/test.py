from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class DataTableItem(QtWidgets.QTableWidgetItem):
    class Signaller(QtCore.QObject):
        signal = QtCore.pyqtSignal(object, str)

        def trigger(self, caller, value):
            self.signal.emit(caller, value)

    def __init__(self):
        super().__init__()
        self.dataChanged = DataTableItem.Signaller()

    def setData(self, role, value):
        if role == QtCore.Qt.EditRole:
            self.dataChanged.trigger(self, value)
        else:
            super().setData(role, value)

class DataTableRow(QtCore.QObject):
    def __init__(self, n):
        super().__init__()

        self.items = []
        self.data = []
        self.name = None
        for i in range(3):
            item = DataTableItem()
            item.setText(str(0))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            item.dataChanged.signal.connect(self.item_modified)

            self.items.append(item)
            self.data.append(0)

        item = QtWidgets.QPushButton('Delete')
        item.clicked.connect(self.delete_clicked)
        self.items.append(item)

    def set_name(self, val):
        self.name = val

    @QtCore.pyqtSlot()
    def delete_clicked(self):
        if self.name is not None:
            del self.parent()[self.name]

    @QtCore.pyqtSlot(object, str)
    def item_modified(self, item, value):
        idx = self.items.index(item)
        self.__setitem__(idx, value)

    def get_row(self):
        return self.items[0].row()

    def get_items(self):
        return self.items

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        try:
            self.data[key] = float(value)
        except:
            pass

        self.items[key].setText(str(self.data[key]))

    def __str__(self):
        return str(self.data)

class DataTable(QtWidgets.QTableWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.rows = {}

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, key):
        return self.rows[key]

    def __setitem__(self, name, row_data):
        row = table.rowCount()
        table.insertRow(row)

        row_data.setParent(self)
        row_data.set_name(name)

        header = QtWidgets.QTableWidgetItem()
        header.setTextAlignment(QtCore.Qt.AlignLeft)
        header.setText(str(name))

        table.setVerticalHeaderItem(row, header)

        for i,item in enumerate(row_data.get_items()):
            if isinstance(item, QtWidgets.QWidget):
                table.setCellWidget(row, i, item)
            else:
                table.setItem(row, i, item)

        if name in self.rows.keys():
            self.__delitem__(name)

        self.rows[name] = row_data

    def __delitem__(self, name):
        if name in self.rows.keys():
            data = self.rows[name]
            self.removeRow(data.get_row())
            del self.rows[name]

    def __iter__(self):
        for k, v in self.rows.items():
            yield k, v

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()

    central = QtWidgets.QWidget(win)
    win.setCentralWidget(central)

    table = DataTable(central)
    table.setGeometry(QtCore.QRect(0, 0, 580, 300))
    table.setColumnCount(4)
    table.setShowGrid(False)

    for i,s in enumerate(['X', 'Y', 'Z']):
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setText(s)
        table.setHorizontalHeaderItem(i, item)

    def to_letter(x):
        ret = []
        first = True
        while x:
            ret += [chr(ord('A') + (x % 26) - (0 if first else 1))]
            first = False
            x //= 26

        if not ret:
            ret = ['A']

        return ''.join(ret[::-1])

    class Point(DataTableRow):
        def __init__(self):
            super().__init__(3)

            flags = self.items[2].flags() & ~QtCore.Qt.ItemIsEditable
            self.items[2].setFlags(flags)

            self.items[0].dataChanged.signal.connect(self.recalc)
            self.items[1].dataChanged.signal.connect(self.recalc)

        @QtCore.pyqtSlot(object, str)
        def recalc(self, item, val):
            self.__setitem__(2, (self.data[0] ** 2 + self.data[1] ** 2) ** .5)

    idx = 0
    def add_point():
        global idx
        table[to_letter(idx)] = Point()
        idx += 1

    button = QtWidgets.QPushButton('New', central)
    button.setGeometry(QtCore.QRect(0, 400, 100, 20))
    button.clicked.connect(add_point)

    print(button.pos())

    win.show()
    rc = app.exec_()
    
    for k, v in table:
        print(k, v)

    sys.exit(rc)
