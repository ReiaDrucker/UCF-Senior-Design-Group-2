from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1567, 1062)
        MainWindow.setMouseTracking(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.photo = QtWidgets.QLabel(self.centralwidget)
        self.photo.setGeometry(QtCore.QRect(20, 10, 981, 961))
        font = QtGui.QFont()
        font.setPointSize(36)
        self.photo.setFont(font)
        self.photo.setText("")
        self.photo.setPixmap(QtGui.QPixmap("test_Image.png"))
        self.photo.setScaledContents(False)
        self.photo.setObjectName("photo")
        self.tableWidgetPoints = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetPoints.setGeometry(QtCore.QRect(900, 70, 601, 351))
        self.tableWidgetPoints.setObjectName("tableWidgetPoints")
        self.tableWidgetPoints.setColumnCount(3)
        self.tableWidgetPoints.setRowCount(2)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetPoints.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setItem(1, 2, item)
        self.tableWidgetVectors = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetVectors.setGeometry(QtCore.QRect(900, 500, 601, 351))
        self.tableWidgetVectors.setObjectName("tableWidgetVectors")
        self.tableWidgetVectors.setColumnCount(4)
        self.tableWidgetVectors.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetVectors.setItem(0, 3, item)
        self.pushButtonAdd_Dummy_Point = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAdd_Dummy_Point.setGeometry(QtCore.QRect(900, 430, 151, 28))
        self.pushButtonAdd_Dummy_Point.setObjectName("pushButtonAdd_Dummy_Point")
        self.pushButtonAdd_Dummy_Vector = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAdd_Dummy_Vector.setGeometry(QtCore.QRect(900, 860, 151, 28))
        self.pushButtonAdd_Dummy_Vector.setObjectName("pushButtonAdd_Dummy_Vector")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1567, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuUpload_Images = QtWidgets.QMenu(self.menubar)
        self.menuUpload_Images.setObjectName("menuUpload_Images")
        self.menuToggle_Display_Options = QtWidgets.QMenu(self.menubar)
        self.menuToggle_Display_Options.setObjectName("menuToggle_Display_Options")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionExport_Data = QtWidgets.QAction(MainWindow)
        self.actionExport_Data.setObjectName("actionExport_Data")
        self.actionUpload_Left = QtWidgets.QAction(MainWindow)
        self.actionUpload_Left.setObjectName("actionUpload_Left")
        self.actionUpload_Right = QtWidgets.QAction(MainWindow)
        self.actionUpload_Right.setObjectName("actionUpload_Right")
        self.actionShow_Vectors = QtWidgets.QAction(MainWindow)
        self.actionShow_Vectors.setObjectName("actionShow_Vectors")
        self.actionShow_Left_Image = QtWidgets.QAction(MainWindow)
        self.actionShow_Left_Image.setObjectName("actionShow_Left_Image")
        self.actionShow_Right_Image = QtWidgets.QAction(MainWindow)
        self.actionShow_Right_Image.setObjectName("actionShow_Right_Image")
        self.actionShow_Interpolated_Image = QtWidgets.QAction(MainWindow)
        self.actionShow_Interpolated_Image.setObjectName("actionShow_Interpolated_Image")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionExport_Data)
        self.menuUpload_Images.addAction(self.actionUpload_Left)
        self.menuUpload_Images.addAction(self.actionUpload_Right)
        self.menuToggle_Display_Options.addAction(self.actionShow_Vectors)
        self.menuToggle_Display_Options.addAction(self.actionShow_Left_Image)
        self.menuToggle_Display_Options.addAction(self.actionShow_Right_Image)
        self.menuToggle_Display_Options.addAction(self.actionShow_Interpolated_Image)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuUpload_Images.menuAction())
        self.menubar.addAction(self.menuToggle_Display_Options.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Stereogram Depth Finder"))
        item = self.tableWidgetPoints.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "Point 1"))
        item = self.tableWidgetPoints.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "Point 2"))
        item = self.tableWidgetPoints.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.tableWidgetPoints.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Pixel Coordinates"))
        item = self.tableWidgetPoints.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Real Coordinates"))
        __sortingEnabled = self.tableWidgetPoints.isSortingEnabled()
        self.tableWidgetPoints.setSortingEnabled(False)
        item = self.tableWidgetPoints.item(0, 0)
        item.setText(_translate("MainWindow", "A"))
        item = self.tableWidgetPoints.item(0, 1)
        item.setText(_translate("MainWindow", "(0, 0)"))
        item = self.tableWidgetPoints.item(0, 2)
        item.setText(_translate("MainWindow", "(0, 0, 0)"))
        item = self.tableWidgetPoints.item(1, 0)
        item.setText(_translate("MainWindow", "B"))
        item = self.tableWidgetPoints.item(1, 1)
        item.setText(_translate("MainWindow", "(1, 0)"))
        item = self.tableWidgetPoints.item(1, 2)
        item.setText(_translate("MainWindow", "(1, 0, 0)"))
        self.tableWidgetPoints.setSortingEnabled(__sortingEnabled)
        item = self.tableWidgetVectors.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "Vector 1"))
        item = self.tableWidgetVectors.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.tableWidgetVectors.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Pixel Coordinates"))
        item = self.tableWidgetVectors.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Real Coordinates"))
        item = self.tableWidgetVectors.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Magnitude"))
        __sortingEnabled = self.tableWidgetVectors.isSortingEnabled()
        self.tableWidgetVectors.setSortingEnabled(False)
        item = self.tableWidgetVectors.item(0, 0)
        item.setText(_translate("MainWindow", "AB"))
        item = self.tableWidgetVectors.item(0, 1)
        item.setText(_translate("MainWindow", "(1, 0)"))
        item = self.tableWidgetVectors.item(0, 2)
        item.setText(_translate("MainWindow", "(1, 0, 0)"))
        item = self.tableWidgetVectors.item(0, 3)
        item.setText(_translate("MainWindow", "1"))
        self.tableWidgetVectors.setSortingEnabled(__sortingEnabled)
        self.pushButtonAdd_Dummy_Point.setText(_translate("MainWindow", "Add Dummy Point"))
        self.pushButtonAdd_Dummy_Vector.setText(_translate("MainWindow", "Add Dummy Vector"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuUpload_Images.setTitle(_translate("MainWindow", "Upload Images"))
        self.menuToggle_Display_Options.setTitle(_translate("MainWindow", "Toggle Display Options"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionOpen.setStatusTip(_translate("MainWindow", "Open a file"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setStatusTip(_translate("MainWindow", "Save a file"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As"))
        self.actionSave_As.setStatusTip(_translate("MainWindow", "Save this file as a new file"))
        self.actionExport_Data.setText(_translate("MainWindow", "Export Data"))
        self.actionExport_Data.setStatusTip(_translate("MainWindow", "Export vector related data"))
        self.actionUpload_Left.setText(_translate("MainWindow", "Upload Left"))
        self.actionUpload_Left.setStatusTip(_translate("MainWindow", "Upload the left half of a stereogram pair"))
        self.actionUpload_Right.setText(_translate("MainWindow", "Upload Right"))
        self.actionUpload_Right.setStatusTip(_translate("MainWindow", "Upload the right half of a stereogram pair"))
        self.actionShow_Vectors.setText(_translate("MainWindow", "Toggle Vector Display"))
        self.actionShow_Left_Image.setText(_translate("MainWindow", "Show Left Image"))
        self.actionShow_Right_Image.setText(_translate("MainWindow", "Show Right Image"))
        self.actionShow_Interpolated_Image.setText(_translate("MainWindow", "Show Interpolated Image"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
