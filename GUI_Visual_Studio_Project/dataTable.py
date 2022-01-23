from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class DataTableItem(QtWidgets.QTableWidgetItem):
    class Signaller(QtCore.QObject):
        signal = QtCore.pyqtSignal(object)

        def trigger(self, caller):
            self.signal.emit(caller)

    def __init__(self, value, from_string, to_string):
        super().__init__()

        self.from_string = from_string
        self.to_string = to_string
        self.dataChanged = DataTableItem.Signaller()

        self.setValue(value)

    def setValue(self, value):
        self.value = value
        self.setText(self.to_string(value))
        self.dataChanged.trigger(self)

    def setData(self, role, value):
        if role == QtCore.Qt.EditRole:
            try:
                self.value = self.from_string(value)
                self.dataChanged.trigger(self)
                super().setData(role, value)
            except:
                pass

        else:
            super().setData(role, value)

class DataTableRow(QtCore.QObject):
    def __init__(self):
        super().__init__()

        self.items = {}
        self.keys = []
        self.name = None

    def set_name(self, val):
        self.name = val

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        # maintain order
        if key not in self.items:
            self.keys += [key]

        self.items[key] = value

    def __getattr__(self, key):
        try:
            items = super().__dict__['items']
            return items[key].value
        except:
            pass

        return super().__getattr__(key)

    def __setattr__(self, key, value):
        try:
            items = super().__dict__['items']
            items[key].setValue(value)
            return
        except:
            pass

        super().__setattr__(key, value)

    def create_field(self, value='', from_string=lambda x: x, to_string=str, editable=True):
        item = DataTableItem(value, from_string, to_string)

        if not editable:
            flags = item.flags()
            item.setFlags(flags & ~QtCore.Qt.ItemIsEditable)

        return item

    def delete(self):
        if self.name is not None:
            del self.parent()[self.name]

    def get_row(self):
        if len(self.items) < 1:
            return -1

        first = next(iter(self.items.keys()))
        return self.items[first].row()

    def get_items(self):
        for key in self.keys:
            yield self.items[key]

    def __str__(self):
        return str({k: v.value for k,v in self.items.items() if hasattr(v, 'value')})

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
            if isinstance(item, QtWidgets.QTableWidgetItem):
                table.setItem(row, i, item)
            else:
                table.setCellWidget(row, i, item)

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

# test
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()

    central = QtWidgets.QWidget(win)
    win.setCentralWidget(central)

    table = DataTable(central)
    table.setGeometry(QtCore.QRect(0, 0, 580, 300))
    table.setColumnCount(20)
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
            super().__init__()

            for field in 'xy':
                self[field] = self.create_field(0, float)
                self[field].dataChanged.signal.connect(self.recalc)

            self['z'] = self.create_field(0, float, editable = False)
            self['z'].dataChanged.signal.connect(self.panic)

            self['D'] = QtWidgets.QPushButton('Delete')
            self['D'].clicked.connect(self.delete)

        @QtCore.pyqtSlot(object)
        def recalc(self, item):
            self.z = (self.x ** 2 + self.y ** 2) ** .5

        @QtCore.pyqtSlot(object)
        def panic(self):
            print('z changed')

    idx = 0
    def add_point():
        global idx
        table[to_letter(idx)] = Point()
        idx += 1

    button = QtWidgets.QPushButton('New', central)
    button.setGeometry(QtCore.QRect(0, 400, 100, 20))
    button.clicked.connect(add_point)

    win.show()
    rc = app.exec_()

    for k, v in table:
        print(k, v)

    sys.exit(rc)
