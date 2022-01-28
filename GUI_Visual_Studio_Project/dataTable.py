from PyQt5 import QtCore, QtGui, QtWidgets
import sys

import traceback

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

        try:
            self.setText(self.to_string(value))
        except RuntimeError:
            # Object deleted?
            return

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
    deleted = QtCore.pyqtSignal()

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
        except KeyError:
            pass

        return super().__dict__[key]

    def __setattr__(self, key, value):
        try:
            items = super().__dict__['items']
            items[key].setValue(value)
            return
        except KeyError:
            pass

        super().__dict__[key] = value

    def create_field(self, value='', from_string=lambda x: x, to_string=str, editable=True):
        item = DataTableItem(value, from_string, to_string)

        if not editable:
            flags = item.flags()
            item.setFlags(flags & ~QtCore.Qt.ItemIsEditable)

        return item

    def delete(self):
        self.deleted.emit()
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
        return str({k: str(v.value) for k,v in self.items.items() if hasattr(v, 'value')})

class DataTable(QtWidgets.QTableWidget):
    onChange = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.cellChanged.connect(lambda x, y: self.onChange.emit())
        self.rows = {}

    def __len__(self):
        return len(self.rows)

    def row_name(self, idx):
        return self.verticalHeaderItem(idx).text()

    def __getitem__(self, key):
        return self.rows[key]

    def __setitem__(self, name, row_data):
        row = self.rowCount()
        self.insertRow(row)

        row_data.setParent(self)
        row_data.set_name(name)

        header = QtWidgets.QTableWidgetItem()
        header.setTextAlignment(QtCore.Qt.AlignLeft)
        header.setText(str(name))

        self.setVerticalHeaderItem(row, header)

        for i,item in enumerate(row_data.get_items()):
            if isinstance(item, QtWidgets.QTableWidgetItem):
                self.setItem(row, i, item)
            else:
                self.setCellWidget(row, i, item)

        if name in self.rows.keys():
            self.__delitem__(name)

        self.rows[name] = row_data
        self.onChange.emit()

    def __delitem__(self, name):
        if name in self.rows.keys():
            data = self.rows[name]

            self.removeRow(data.get_row())
            del self.rows[name]
        self.onChange.emit()

    def __iter__(self):
        for k, v in self.rows.items():
            yield k, v

class DataTableWidget(QtWidgets.QWidget):
    onNew = QtCore.pyqtSignal()

    def __init__(self, columns, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()

        self.__table = DataTable(parent=self)
        self.__table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.__table.onChange.connect(self.resize)

        layout.addWidget(self.__table)

        self.__table.setColumnCount(len(columns))
        for i,column in enumerate(columns):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setText(column)

            self.__table.setHorizontalHeaderItem(i, item)

        hlayout = QtWidgets.QHBoxLayout()

        self._button = QtWidgets.QPushButton('New')
        self._button.clicked.connect(self.onNew.emit)
        hlayout.addWidget(self._button)
        hlayout.addStretch()

        layout.addLayout(hlayout)

        self.setLayout(layout)

    @QtCore.pyqtSlot()
    def resize(self):
        self.__table.resizeColumnsToContents()

    def get_table(self):
        return self.__table

# test
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()

    central = QtWidgets.QWidget(win)
    win.setCentralWidget(central)

    layout = QtWidgets.QVBoxLayout()

    point_table_widget = DataTableWidget(['X', 'Y', ''], parent=central)
    layout.addWidget(point_table_widget)
    point_table = point_table_widget.get_table()

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
        dataChanged = QtCore.pyqtSignal()

        def __init__(self):
            super().__init__()

            for field in 'xy':
                self[field] = self.create_field(0, float)
                self[field].dataChanged.signal.connect(self.dataChanged.emit)

            self['D'] = QtWidgets.QPushButton('Delete')
            self['D'].clicked.connect(self.delete)

    idx = 0
    def add_point():
        global idx
        point_table[to_letter(idx)] = Point()
        idx += 1

    point_table_widget.onNew.connect(add_point)

    vector_table_widget = DataTableWidget(['S', 'T', 'Dist', ''], parent=central)
    layout.addWidget(vector_table_widget)
    vector_table = vector_table_widget.get_table()

    class Vector(DataTableRow):
        def __init__(self, s, t):
            super().__init__()

            def updater(key):
                @QtCore.pyqtSlot()
                def func():
                    self.__setattr__(key, self.sender())
                    self.dist = self.get_dist()
                return func

            self['s'] = self.create_field(s, editable=False)
            s.dataChanged.connect(updater('s'))
            s.deleted.connect(self.delete)

            self['t'] = self.create_field(t, editable=False)
            t.dataChanged.connect(updater('t'))
            t.deleted.connect(self.delete)

            self['dist'] = self.create_field(self.get_dist(), float, editable=False)

        def get_dist(self):
            dx = self.s.x - self.t.x
            dy = self.s.y - self.t.y
            return (dx ** 2 + dy ** 2) ** .5

    idx2 = 0
    def add_vector():
        global idx2
        selected = list(set(point_table.row_name(x.row()) for x in point_table.selectedItems()))
        if len(selected) == 2:
            vector_table[to_letter(idx2)] = Vector(point_table[selected[0]], point_table[selected[1]])
            idx2 += 1

    vector_table_widget.onNew.connect(add_vector)

    central.setLayout(layout)
    win.show()
    rc = app.exec_()

    for k, v in point_table:
        print(k, v)

    for k, v in vector_table:
        print(k, v)

    sys.exit(rc)
