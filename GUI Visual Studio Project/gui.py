import os
import cv2 as cv
from PyQt5 import QtCore, QtGui, QtWidgets

from photoDisplayer import *
from pointDialog import *
from vectorDialog import *
from real import *

from deleteVectorDialog import *
from deletePointDialog import *
from editPointDialog import *
from editVectorDialog import *
from changeColorDialog import *
import pickle
import os

class Ui_MainWindow(QtWidgets.QWidget):

    def setupUi(self, MainWindow):
        self.leftImage = None
        self.rightImage = None

        # Window sizes should be based on the monitor resolution rather than a hard coded pixel value.
        MainWindow.resize(1600, 1000)
        MainWindow.setMouseTracking(True)
        MainWindow.setWindowTitle("Stereogram Depth Finder")
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

        # Sets the widget in the center
        MainWindow.setCentralWidget(self.centralwidget)

        # Creates menu bar.
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1567, 26))

        # Menu options.
        self.menuFile = QtWidgets.QMenu("File", self.menubar)
        self.menuUploadImages = QtWidgets.QMenu("Upload Images", self.menubar)
        self.menuToggleDisplayOptions = QtWidgets.QMenu("Toggle Display Options", self.menubar)
        
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionOpen = QtWidgets.QAction("Open", MainWindow)
        self.actionOpen.setStatusTip("Open a file")
        self.actionOpen.triggered.connect(self.loadGUIFromFile)

        # TODO: Action button not connected to anything yet.
        self.actionSave = QtWidgets.QAction("Save", MainWindow)
        self.actionSave.setStatusTip("Save a file")
        self.actionSave.setShortcut("Ctrl+S")

        self.actionSaveAs = QtWidgets.QAction("Save As", MainWindow)
        self.actionSaveAs.setStatusTip("Save this file as a new file")
        self.actionSaveAs.triggered.connect(self.saveGUIToFile)

        self.actionExportData = QtWidgets.QAction("Export Data", MainWindow)
        self.actionExportData.setStatusTip("Exports the data")

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
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionExportData)

        self.menuUploadImages.addAction(self.actionUploadLeft)
        self.menuUploadImages.addAction(self.actionUploadRight)

        self.menuToggleDisplayOptions.addAction(self.actionShowVectors)
        self.menuToggleDisplayOptions.addAction(self.actionShowLeftImage)
        self.menuToggleDisplayOptions.addAction(self.actionShowRightImage)
        self.menuToggleDisplayOptions.addAction(self.actionShowInterpolatedImage)
        
        # Add menus to menu bar.
        self.menubar.addMenu(self.menuFile)
        self.menubar.addMenu(self.menuUploadImages)
        self.menubar.addMenu(self.menuToggleDisplayOptions)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

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
            
    # Adds point row to point table widget.
    def addPoint(self):
        dialog = pointDialog(self.pd)
        dialog.exec()
                
    # Adds vector row to vector table widget.
    def addVector(self):
        dialog = vectorDialog(self.pd)
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

    def displayReal(self):
        if self.leftImage and self.rightImage:
            real = getRealFromImages(self.leftImage, self.rightImage)
            self.pd.setNewReal(real)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
