from PyQt5 import QtCore, QtGui, QtWidgets
from photoDisplayer import *
from pointDialog import *
from vectorDialog import *
from deleteVectorDialog import *
from deletePointDialog import *
from changeColorDialog import *
import os

class Ui_MainWindow(QtWidgets.QWidget):

    def setupUi(self, MainWindow):

        self.leftImagePath = ""
        self.rightImagePath = ""

        # Window initialization.
        MainWindow.setObjectName("MainWindow")

        # Window sizes should be based on the monitor resolution rather than a hard coded pixel value.
        MainWindow.resize(1600, 1000)
        MainWindow.setMouseTracking(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Set up point table.
        self.pointTable = QtWidgets.QTableWidget(self.centralwidget)
        self.pointTable.setGeometry(QtCore.QRect(1000, 70, 580, 300))
        self.pointTable.setObjectName("pointTable")
        self.pointTable.setColumnCount(3)
        self.pointTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Set up columns for point table.
        for i in range(3):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.pointTable.setHorizontalHeaderItem(i, item)
        self.pointTable.horizontalHeaderItem(0).setText("Name")
        self.pointTable.horizontalHeaderItem(1).setText("Pixel Coordinates")
        self.pointTable.horizontalHeaderItem(2).setText("Real Coordinates")

        # Set up vector tables.
        self.vectorTable = QtWidgets.QTableWidget(self.centralwidget)
        self.vectorTable.setGeometry(QtCore.QRect(1000, 500, 580, 300))
        self.vectorTable.setObjectName("vectorTable")
        self.vectorTable.setColumnCount(4)
        self.vectorTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Set up columns for vector table.
        for i in range(4):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.vectorTable.setHorizontalHeaderItem(i, item)
        self.vectorTable.horizontalHeaderItem(0).setText("Name")
        self.vectorTable.horizontalHeaderItem(1).setText("Pixel Coordinates")
        self.vectorTable.horizontalHeaderItem(2).setText("Real Coordinates")
        self.vectorTable.horizontalHeaderItem(3).setText("Magnitude")

        # Uploading and drawing image onto interface.
        self.pd = PhotoDisplayer(960, 540, self.pointTable, self.vectorTable, self.centralwidget)
        self.pd.setGeometry(QtCore.QRect(20, 10, 960, 540))
        self.pd.setObjectName("photoDisplay")

        self.pushButtonChange_Vector_Color = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonChange_Vector_Color.setGeometry(QtCore.QRect(1000, 10, 150, 30))
        self.pushButtonChange_Vector_Color.setObjectName("pushButtonChange_Vector_Color")
        self.pushButtonChange_Vector_Color.clicked.connect(lambda: self.changeColor(0))

        self.pushButtonChange_Point_Color = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonChange_Point_Color.setGeometry(QtCore.QRect(1200, 10, 150, 30))
        self.pushButtonChange_Point_Color.setObjectName("pushButtonChange_Point_Color")
        self.pushButtonChange_Point_Color.clicked.connect(lambda: self.changeColor(1))

        # Buttons for points.
        self.buttonAddPoint = QtWidgets.QPushButton("Add Point", self.centralwidget)
        self.buttonDeletePoint = QtWidgets.QPushButton("Delete Point", self.centralwidget)
        self.buttonEditPoint = QtWidgets.QPushButton("Edit Point", self.centralwidget)

        self.buttonAddPoint.setGeometry(QtCore.QRect(1000, 400, 150, 30))
        self.buttonDeletePoint.setGeometry(QtCore.QRect(1200, 400, 150, 30))
        self.buttonEditPoint.setGeometry(QtCore.QRect(1400, 400, 150, 30))

        self.buttonAddPoint.clicked.connect(self.addPoint)
        self.buttonDeletePoint.clicked.connect(self.deletePoint)
        self.buttonEditPoint.clicked.connect(self.deletePoint)

        # Buttons for vectors.
        self.buttonAddVector = QtWidgets.QPushButton("Add Vector", self.centralwidget)
        self.buttonDeleteVector = QtWidgets.QPushButton("Delete Vector", self.centralwidget)
        self.buttonEditVector = QtWidgets.QPushButton("Edit Vector", self.centralwidget)

        self.buttonAddVector.setGeometry(QtCore.QRect(1000, 830, 150, 30))
        self.buttonDeleteVector.setGeometry(QtCore.QRect(1200, 830, 150, 30))
        self.buttonEditVector.setGeometry(QtCore.QRect(1400, 830, 150, 30))

        self.buttonAddVector.clicked.connect(self.addVector)      
        self.buttonDeleteVector.clicked.connect(self.deleteVector)
        self.buttonEditVector.clicked.connect(self.deletePoint)

        # Sets the widget in the center
        MainWindow.setCentralWidget(self.centralwidget)

        # Creates menu bar.
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1567, 26))

        self.menuFile = QtWidgets.QMenu("File", self.menubar)
        self.menuUploadImages = QtWidgets.QMenu("Upload Images", self.menubar)
        self.menuToggleDisplayOptions = QtWidgets.QMenu("Toggle Display Options", self.menubar)
        
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
        self.menuUploadImages.addAction(self.actionUpload_Left)
        self.menuUploadImages.addAction(self.actionUpload_Right)
        self.menuToggleDisplayOptions.addAction(self.actionShow_Vectors)
        self.menuToggleDisplayOptions.addAction(self.actionShow_Left_Image)
        self.menuToggleDisplayOptions.addAction(self.actionShow_Right_Image)
        self.menuToggleDisplayOptions.addAction(self.actionShow_Interpolated_Image)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuUploadImages.menuAction())
        self.menubar.addAction(self.menuToggleDisplayOptions.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # Basically names everything.
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Stereogram Depth Finder"))

        # Names row and column items of point table.
        #self.pointTable.setSortingEnabled(False)

        # Names row and column items of vector table.
        #__sortingEnabled = self.vectorTable.isSortingEnabled()
        #self.vectorTable.setSortingEnabled(False)

        # Names buttons to add rows to tables.
        self.pushButtonChange_Vector_Color.setText(_translate("MainWindow", "Select Vector Color"))
        self.pushButtonChange_Point_Color.setText(_translate("MainWindow", "Select Point Color"))

        # Names all of the menu bar actions.
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

    def uploadLeftImage(self):
        fname = "Image File (*.jpeg *.jpg *.png *.gif *.tif *.tiff)"
        newName = QtWidgets.QFileDialog.getOpenFileName(self, "Select an image file", os.getcwd(), fname, fname)

        # Don't update if they didn't select an image
        # Probably also don't want to update if they select the same image
        if(newName[0] != ""):
            self.leftImagePath = newName[0]
            self.pd.setNewPixmap(QtGui.QPixmap(newName[0]))
            self.update()

    def uploadRightImage(self):
        fname = "Image File (*.jpeg *.jpg *.png *.gif *.tif *.tiff)"
        newName = QtWidgets.QFileDialog.getOpenFileName(self, "Select an image file", os.getcwd(), fname, fname)

        # Don't update if they didn't select an image
        # Probably also don't want to update if they select the same image
        if(newName[0] != ""):
            self.rightImagePath = newName[0]
            self.pd.setNewPixmap(QtGui.QPixmap(newName[0]))
            self.update()

    def displayImage(self, selection):
        if(selection == 0 and self.leftImagePath != None):
            self.pd.setNewPixmap(QtGui.QPixmap(self.leftImagePath))
            self.update()
        if(selection == 1 and self.rightImagePath != None):
            self.pd.setNewPixmap(QtGui.QPixmap(self.rightImagePath))
            self.update()
        
    # Adds dummy point row to point table widget.
    def addPoint(self):
        dialog = pointDialog(self)
        dialog.exec()
                
    # Adds dummy vector row to vector table widget.
    def addVector(self):
        dialog = vectorDialog(self)
        dialog.exec()
    
    # Deletes vector from vector table.
    def deleteVector(self):
        dialog = deleteVectorDialog(self)
        dialog.exec()

    # Deletes point from point table.
    def deletePoint(self):
        dialog = deletePointDialog(self)
        dialog.exec()

    def changeColor(self, changeType):
        dialog = changeColorDialog(self, changeType)
        dialog.exec()

if __name__ == "__main__":
    import sys
    import math
    from point import *
    from vector import *
    import numpy as np

    p1 = Point("A", 0, 0, 0, 0, 0)
    p2 = Point("B", 0, 1, 4, 6, 7)
    p3 = Point("C", 1, 2, 3, 4, 5)
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
