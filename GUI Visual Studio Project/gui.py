import os
import cv2 as cv
from PyQt5 import QtCore, QtGui, QtWidgets

from photoDisplayer import *
from pointDialog import *
from vectorDialog import *
from real import *

class Ui_MainWindow(QtWidgets.QWidget):

    def setupUi(self, MainWindow):
        self.leftImage = None
        self.rightImage = None

        # Window initialization.
        MainWindow.setObjectName("MainWindow")

        # TODO: Window sizes should be based on the monitor resolution rather than a hard coded pixel value
        MainWindow.resize(1600, 1000)
        MainWindow.setMouseTracking(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")



        # Initialize point table for storing points.
        self.tableWidgetPoints = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetPoints.setGeometry(QtCore.QRect(1000, 70, 580, 300))
        self.tableWidgetPoints.setObjectName("tableWidgetPoints")
        self.tableWidgetPoints.setColumnCount(3)

        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetPoints.setHorizontalHeaderItem(2, item)

        self.tableWidgetVectors = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetVectors.setGeometry(QtCore.QRect(1000, 500, 580, 300))
        self.tableWidgetVectors.setObjectName("tableWidgetVectors")
        self.tableWidgetVectors.setColumnCount(4)
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

        # Uploading and drawing image onto interface.
        self.pd = PhotoDisplayer(960, 540, self.tableWidgetPoints, self.tableWidgetVectors, self.centralwidget)
        self.pd.setGeometry(QtCore.QRect(20, 10, 960, 540))
        self.pd.setObjectName("photoDisplay")

        # Button to add dummy point.
        self.pushButtonAdd_Dummy_Point = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAdd_Dummy_Point.setGeometry(QtCore.QRect(1000, 400, 150, 30))
        self.pushButtonAdd_Dummy_Point.setObjectName("pushButtonAdd_Dummy_Point")
        self.pushButtonAdd_Dummy_Point.clicked.connect(self.addDummyPoint)

        self.pushButtonAdd_Dummy_Vector = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAdd_Dummy_Vector.setGeometry(QtCore.QRect(1000, 800, 150, 30))
        self.pushButtonAdd_Dummy_Vector.setObjectName("pushButtonAdd_Dummy_Vector")
        self.pushButtonAdd_Dummy_Vector.clicked.connect(self.addDummyVector)

        # Sets the widget in the center
        MainWindow.setCentralWidget(self.centralwidget)

        # Creates menu bar.
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
        self.actionUpload_Left.triggered.connect(self.uploadLeftImage)
        self.actionUpload_Left.setObjectName("actionUpload_Left")

        self.actionUpload_Right = QtWidgets.QAction(MainWindow)
        self.actionUpload_Right.triggered.connect(self.uploadRightImage)
        self.actionUpload_Right.setObjectName("actionUpload_Right")

        # When you click this toggle is switches whether points and vectors are displayed
        self.actionShow_Vectors = QtWidgets.QAction(MainWindow)
        self.actionShow_Vectors.triggered.connect(self.pd.toggleDraw)
        self.actionShow_Vectors.setObjectName("actionShow_Vectors")

        # When you click we switch to the left image
        self.actionShow_Left_Image = QtWidgets.QAction(MainWindow)
        self.actionShow_Left_Image.triggered.connect(lambda: self.displayImage(0))
        self.actionShow_Left_Image.setObjectName("actionShow_Left_Image")

        # When you click we switch to the right image
        self.actionShow_Right_Image = QtWidgets.QAction(MainWindow)
        self.actionShow_Right_Image.triggered.connect(lambda: self.displayImage(1))
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

    # Basically names everything.
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Stereogram Depth Finder"))

        # Names row and column items of point table.
        item = self.tableWidgetPoints.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.tableWidgetPoints.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Pixel Coordinates"))
        item = self.tableWidgetPoints.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Real Coordinates"))
        self.tableWidgetPoints.setSortingEnabled(False)

        # Names row and column items of vector table.
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

        # Names buttons to add rows to tables.
        self.pushButtonAdd_Dummy_Point.setText(_translate("MainWindow", "Add Dummy Point"))
        self.pushButtonAdd_Dummy_Vector.setText(_translate("MainWindow", "Add Dummy Vector"))

        # Names all of the menu bar actions.
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

    def loadImage(self, path):
        img = cv.imread(path, cv.IMREAD_COLOR)

        # Resize to fit in the photo viewer
        # FIXME: this will break whenever resizing is implemented
        #   Ideally the photo displayers coordinate system should be separate from our points
        s = max(img.shape[1] / self.pd.geometry().width(), img.shape[0] / self.pd.geometry().height())
        shape = np.int0([img.shape[1] / s, img.shape[0] / s])
        img = cv.resize(img, shape)

        print(img.shape)

        return QtGui.QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QtGui.QImage.Format_BGR888)


    def uploadLeftImage(self):
        fname = "Image File (*.jpeg *.jpg *.png *.gif *.tif *.tiff)"
        newName = QtWidgets.QFileDialog.getOpenFileName(self, "Select an image file", os.getcwd(), fname, fname)

        # Don't update if they didn't select an image
        # Probably also don't want to update if they select the same image
        if(newName[0] != ""):
            self.leftImage = self.loadImage(newName[0])
            self.pd.setNewPixmap(QtGui.QPixmap(self.leftImage))
            self.displayReal()
            self.update()

    def uploadRightImage(self):
        fname = "Image File (*.jpeg *.jpg *.png *.gif *.tif *.tiff)"
        newName = QtWidgets.QFileDialog.getOpenFileName(self, "Select an image file", os.getcwd(), fname, fname)

        # Don't update if they didn't select an image
        # Probably also don't want to update if they select the same image
        if(newName[0] != ""):
            self.rightImage = self.loadImage(newName[0])
            self.pd.setNewPixmap(QtGui.QPixmap(self.rightImage))
            self.displayReal()
            self.update()

    def displayImage(self, selection):
        if(selection == 0 and self.leftImage != None):
            self.pd.setNewPixmap(QtGui.QPixmap(self.leftImage))
            self.update()
        if(selection == 1 and self.rightImage != None):
            self.pd.setNewPixmap(QtGui.QPixmap(self.rightImage))
            self.update()
        
    # Adds dummy point row to point table widget.
    def addDummyPoint(self):
        dialog = pointDialog(self)
        dialog.exec()
                
    # Adds dummy vector row to vector table widget.
    def addDummyVector(self):

        dialog = vectorDialog(self)
        dialog.exec()

    def displayReal(self):
        if self.leftImage and self.rightImage:
            real = getRealFromImages(self.leftImage, self.rightImage)
            self.pd.setNewReal(real)

if __name__ == "__main__":
    import sys
    import math
    from point import *
    from vector import *
    import numpy as np

    p1 = Point("A", 0, 0)
    p2 = Point("B", 6, 7)
    p3 = Point("C", 4, 5)
    #print(p2)

    v1 = Vector(p3,p2)
    #print(v1)
    #v2 = Vector(p1, p3);

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
