from PyQt5 import QtCore, QtGui, QtWidgets
from photoDisplayer import *
from pointDialog import *
from vectorDialog import *
from angleDialog import *
from deleteVectorDialog import *
from deletePointDialog import *
from editPointDialog import *
from editVectorDialog import *
from changeColorDialog import *
from photoDisplayerContainer import *
import pickle
import os

class Ui_MainWindow(QtWidgets.QWidget):

    def setupUi(self, MainWindow):
        # Initialize image paths.
        self.leftImagePath = ""
        self.rightImagePath = ""

        # Window sizes should be based on the monitor resolution rather than a hard coded pixel value.
        MainWindow.resize(1600, 1000)
        MainWindow.setMouseTracking(True)
        MainWindow.setWindowTitle("Stereogram Depth Finder")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Set up point table.
        self.pointTable = QtWidgets.QTableWidget(self.centralwidget)
        self.pointTable.setGeometry(QtCore.QRect(1000, 70, 580, 300))
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

        # Set up angle table.
        self.angleTable = QtWidgets.QTableWidget(self.centralwidget)
        self.angleTable.setGeometry(QtCore.QRect(10, 560, 580, 300))
        self.angleTable.setColumnCount(4)
        self.angleTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Set up columns for angle table.
        for i in range(4):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.angleTable.setHorizontalHeaderItem(i, item)
        self.angleTable.horizontalHeaderItem(0).setText("Name")
        self.angleTable.horizontalHeaderItem(1).setText("Vector 1")
        self.angleTable.horizontalHeaderItem(2).setText("Vector 2")
        self.angleTable.horizontalHeaderItem(3).setText("Angle")

        # Handles drawing of points and vectors along with zoom
        self.pd = PhotoDisplayer(960, 540, self.pointTable, self.vectorTable, self.angleTable)
        self.pdContainer = photoDisplayerContainer(self.centralwidget, self.pd)
        self.pdContainer.setObjectName("pdContainer")
        self.pdContainer.setGeometry(QtCore.QRect(10, 10, 960, 540))

        self.pushButtonChangeVectorColor = QtWidgets.QPushButton("Select Vector Color", self.centralwidget)
        self.pushButtonChangeVectorColor.setGeometry(QtCore.QRect(1000, 10, 150, 30))
        self.pushButtonChangeVectorColor.clicked.connect(lambda: self.changeColor(0))

        self.pushButtonChangePointColor = QtWidgets.QPushButton("Select Point Color", self.centralwidget)
        self.pushButtonChangePointColor.setGeometry(QtCore.QRect(1200, 10, 150, 30))
        self.pushButtonChangePointColor.clicked.connect(lambda: self.changeColor(1))

        # Buttons for points.
        self.buttonAddPoint = QtWidgets.QPushButton("Add Point", self.centralwidget)
        self.buttonDeletePoint = QtWidgets.QPushButton("Delete Point", self.centralwidget)
        self.buttonEditPoint = QtWidgets.QPushButton("Edit Point", self.centralwidget)

        self.buttonAddPoint.setGeometry(QtCore.QRect(1000, 400, 150, 30))
        self.buttonDeletePoint.setGeometry(QtCore.QRect(1200, 400, 150, 30))
        self.buttonEditPoint.setGeometry(QtCore.QRect(1400, 400, 150, 30))

        self.buttonAddPoint.clicked.connect(self.addPoint)
        self.buttonDeletePoint.clicked.connect(self.deletePoint)
        self.buttonEditPoint.clicked.connect(self.editPoint)

        # Buttons for vectors.
        self.buttonAddVector = QtWidgets.QPushButton("Add Vector", self.centralwidget)
        self.buttonDeleteVector = QtWidgets.QPushButton("Delete Vector", self.centralwidget)
        self.buttonEditVector = QtWidgets.QPushButton("Edit Vector", self.centralwidget)

        self.buttonAddVector.setGeometry(QtCore.QRect(1000, 830, 150, 30))
        self.buttonDeleteVector.setGeometry(QtCore.QRect(1200, 830, 150, 30))
        self.buttonEditVector.setGeometry(QtCore.QRect(1400, 830, 150, 30))

        self.buttonAddVector.clicked.connect(self.addVector)      
        self.buttonDeleteVector.clicked.connect(self.deleteVector)
        self.buttonEditVector.clicked.connect(self.editVector)

        # Buttons for angles.
        self.buttonAddAngle = QtWidgets.QPushButton("Add Angle", self.centralwidget)
        self.buttonDeleteAngle = QtWidgets.QPushButton("Delete Angle", self.centralwidget)
        self.buttonEditAngle = QtWidgets.QPushButton("Edit Angle", self.centralwidget)

        self.buttonAddAngle.setGeometry(QtCore.QRect(10, 880, 150, 30))
        self.buttonDeleteAngle.setGeometry(QtCore.QRect(210, 880, 150, 30))
        self.buttonEditAngle.setGeometry(QtCore.QRect(410, 880, 150, 30))

        self.buttonAddAngle.clicked.connect(self.addAngle)
        

        # Sets the widget in the center
        MainWindow.setCentralWidget(self.centralwidget)

        # Creates menu bar.
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1567, 26))

        # Menu options.
        self.menuFile = QtWidgets.QMenu("File", self.menubar)
        self.menuUploadImages = QtWidgets.QMenu("Upload Images", self.menubar)
        self.menuToggleDisplayOptions = QtWidgets.QMenu("Toggle Display Options", self.menubar)
        self.menuZoomOptions = QtWidgets.QMenu("Zoom Options", self.menubar)
        
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionZoomIn = QtWidgets.QAction("Zoom In 25%", MainWindow)
        self.actionZoomIn.setStatusTip("Zoom in on the image")
        self.actionZoomIn.triggered.connect(self.pdContainer.zoomIn)
        self.actionZoomIn.setShortcut("Ctrl+=")

        self.actionZoomOut = QtWidgets.QAction("Zoom Out 25%", MainWindow)
        self.actionZoomOut.setStatusTip("Zoom out on the image")
        self.actionZoomOut.triggered.connect(self.pdContainer.zoomOut)
        self.actionZoomOut.setShortcut("Ctrl+-")

        self.actionZoomReset = QtWidgets.QAction("Reset Zoom", MainWindow)
        self.actionZoomReset.setStatusTip("Restore Image to Normal Size")
        self.actionZoomReset.triggered.connect(self.pdContainer.resetZoom)
        self.actionZoomReset.setShortcut("Ctrl+r")

        self.actionLoadData = QtWidgets.QAction("Load Data", MainWindow)
        self.actionLoadData.setStatusTip("Load Data from SDFDATA File")
        self.actionLoadData.triggered.connect(self.loadGUIFromFile)

        self.actionExportData = QtWidgets.QAction("Export Data", MainWindow)
        self.actionExportData.setStatusTip("Exports the data")
        self.actionExportData.triggered.connect(self.saveGUIToFile)
        self.actionExportData.setShortcut("Ctrl+S")

        self.actionUploadLeft = QtWidgets.QAction("Upload Left", MainWindow)
        self.actionUploadLeft.setStatusTip("Upload left half of a stereogram pair")
        self.actionUploadLeft.triggered.connect(self.uploadLeftImage)

        self.actionUploadRight = QtWidgets.QAction("Upload Right", MainWindow)
        self.actionUploadLeft.setStatusTip("Upload right half of a stereogram pair")
        self.actionUploadRight.triggered.connect(self.uploadRightImage)

        # When you click this toggle is switches whether points and vectors are displayed
        self.actionShowVectors = QtWidgets.QAction("Toggle Vector Display", MainWindow)
        self.actionShowVectors.triggered.connect(self.pd.toggleDraw)

        # When you click we switch to the left image
        self.actionShowLeftImage = QtWidgets.QAction("Show Left Image", MainWindow)
        self.actionShowLeftImage.triggered.connect(lambda: self.displayImage(0))

        # When you click we switch to the right image
        self.actionShowRightImage = QtWidgets.QAction("Show Right Image", MainWindow)
        self.actionShowRightImage.triggered.connect(lambda: self.displayImage(1))

        # TODO: Button not connected yet.
        self.actionShowInterpolatedImage = QtWidgets.QAction("Show Interpolated Image", MainWindow)
        
        # Add actions to menus.
        self.menuFile.addAction(self.actionLoadData)
        self.menuFile.addAction(self.actionExportData)

        self.menuUploadImages.addAction(self.actionUploadLeft)
        self.menuUploadImages.addAction(self.actionUploadRight)

        self.menuToggleDisplayOptions.addAction(self.actionShowVectors)
        self.menuToggleDisplayOptions.addAction(self.actionShowLeftImage)
        self.menuToggleDisplayOptions.addAction(self.actionShowRightImage)
        self.menuToggleDisplayOptions.addAction(self.actionShowInterpolatedImage)

        self.menuZoomOptions.addAction(self.actionZoomIn)
        self.menuZoomOptions.addAction(self.actionZoomOut)
        self.menuZoomOptions.addAction(self.actionZoomReset)


        
        # Add menus to menu bar.
        self.menubar.addMenu(self.menuFile)
        self.menubar.addMenu(self.menuUploadImages)
        self.menubar.addMenu(self.menuToggleDisplayOptions)
        self.menubar.addMenu(self.menuZoomOptions)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

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
        if(selection == 0 and self.leftImagePath != None and os.path.exists(self.leftImagePath)):
            self.pd.setNewPixmap(QtGui.QPixmap(self.leftImagePath))
            self.update()
        if(selection == 1 and self.rightImagePath != None and os.path.exists(self.rightImagePath)):
            self.pd.setNewPixmap(QtGui.QPixmap(self.rightImagePath))
            self.update()
        
    # Adds point row to point table widget.
    def addPoint(self):
        dialog = pointDialog(self.pd)
        dialog.exec()
                
    # Adds vector row to vector table widget.
    def addVector(self):
        dialog = vectorDialog(self.pd)
        dialog.exec()

    # Adds angle row to angle table widget.
    def addAngle(self):
        if self.pd.vectors.size >= 2:
            dialog = angleDialog(self.pd)
            dialog.exec()
    
    # Deletes vector from vector table.
    def deleteVector(self):
        if self.pd.vectors.size > 0:
            dialog = deleteVectorDialog(self.pd)
            dialog.exec()

    # Deletes point from point table.
    def deletePoint(self):
        if self.pd.points.size > 0:
            dialog = deletePointDialog(self.pd)
            dialog.exec()

    # Edits point in point table.
    def editPoint(self):
        if self.pd.points.size > 0:
            dialog = editPointDialog(self.pd)
            dialog.exec()

    def changeColor(self, changeType):
        dialog = changeColorDialog(self, changeType)
        dialog.exec()

    def editVector(self):
        if self.pd.vectors.size > 0:
            dialog = editVectorDialog(self.pd)
            dialog.exec()

    # Write to a file
    # Can't pickle UI_MainWindow need to figure out how to do that
    # Probably best to use QDatastream instead
    def saveGUIToFile(self):
        fname = "SDFDATA File (*.SDFDATA)"
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Select Directory To Save To", os.getcwd(), fname, fname)

        objectToSave = [self.pd.points, self.pd.vectors, self.leftImagePath, self.rightImagePath]

        # If path is valid serialize the data into the file
        if(filePath[0] != ""):
            with open(filePath[0], 'wb') as handle:
                pickle.dump(objectToSave, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Write the data via out

    #Load a file
    # Probably best to use QDatastream instead
    def loadGUIFromFile(self):

        fname = "SDFDATA File (*.SDFDATA)"
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Select an image file", os.getcwd(), fname, fname)

        # Make sure they selected something correct
        if(filePath[0] != "" and filePath[0].endswith(".SDFDATA")):
            with open(filePath[0], 'rb') as handle:
                data = pickle.load(handle)

                # Load point and vecotr data
                self.pd.points = data[0]
                self.pd.vectors = data[1]
                self.pd.updatePointTable()
                self.pd.updateVectorTable()

                # Load image path data
                self.leftImagePath = data[2]
                self.rightImagePath = data[3]
                
                # Tries left and then right
                self.displayImage(0)
                self.displayImage(1)

            # Read the data via inStream

            # Turn off the old UI
            # Return the new one
            return None
        else:
            return None

        

if __name__ == "__main__":
    import sys
    import math
    from point import *
    from vector import *
    import numpy as np

    
    #p1 = Point("A", 0, 0, 0, 0, 0)
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
