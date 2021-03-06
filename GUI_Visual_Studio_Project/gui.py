from PyQt5 import QtCore, QtGui, QtWidgets
from photoDisplayer import *
from editParametersDialog import *
from parameterDialog import *
from photoDisplayerContainer import *
from dataTable import *
from colorSelector import *
from depthProvider import *
from point import *
from vector import *
from angle import *
import pickle
import os
import math

# Creates alphabetic label for tables depending on value x.
def createLabel(x):
    ret = []
    first = True
    while x:
        ret += [chr(ord('A') + (x % 26) - (0 if first else 1))]
        first = False
        x //= 26

    if not ret:
        ret = ['A']

    return ''.join(ret[::-1])

class Ui_MainWindow(QtWidgets.QWidget):
    # Initializes the main window.
    def __init__(self):
        super().__init__()

        # Set table index values to 0.
        self.pointIdx = 0
        self.vectorIdx = 0
        self.angleIdx = 0

        # Initialize empty image paths.
        self.imagePath = [None] * 2
        self.lastDir = None

        # Initialize Depth Provider.
        self.depthProvider = DepthProvider2(self, 45 * math.pi / 180)

    # Creates new table with flexible properties.
    def addTable(self, columns, onNew, x, y, w, h, color=None, onColorChange=None):
        bottom_widgets = []

        # "New" button to click to add new item.
        new_button = QtWidgets.QPushButton('New')
        new_button.clicked.connect(onNew)
        bottom_widgets += [new_button]

        # Determines color.
        if onColorChange is not None:
            color_select = ColorSelector(color)
            color_select.currentIndexChanged.connect(onColorChange)
            bottom_widgets += [color_select]

        # Items are selected by rows, multiple rows can be selected,
        # and cells must be double-clicked to enable editing.
        widget = DataTableWidget(columns, bottom_widgets=bottom_widgets, parent=self.centralwidget)
        widget.get_table().setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        widget.get_table().setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        widget.get_table().setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)

        # Table widget is added to window layout.
        self.layout.addWidget(widget, y, x, h, w)

        # Connect adding function for this table.
        widget.onNew.connect(onNew)
        return widget.get_table()

    # Main setup function for the MainWindow.
    def setupUi(self, MainWindow):
        # Window sizes should be based on the monitor resolution rather than a hard coded pixel value.
        # MainWindow.resize(1600, 1000)

        # Basic properties of the window.
        MainWindow.setMouseTracking(True)
        MainWindow.setWindowTitle("Stereogram Depth Finder")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        self.centralwidget.setObjectName("centralwidget")
        self.layout = QtWidgets.QGridLayout()

        # Initialize PhotoDisplayer and photoDisplayerContainer.
        self.pd = PhotoDisplayer(self)
        self.pd.displayToggle.connect(self.toggleTableEdits)
        self.pdContainer = photoDisplayerContainer(self.centralwidget, self.pd)
        self.pdContainer.setObjectName("pdContainer")
        self.layout.addWidget(self.pdContainer, 0, 0, 2, 2)

        # Change pen color and send information to the PhotoDisplayer.
        def changeColor(pen):
            @QtCore.pyqtSlot(int)
            def f(idx):
                pen.setColor(self.sender().get_color())
                self.pd.update()
            return f

        # Initialize point, vector, and angle tables.
        self.pointTable = self.addTable(['u', 'v', 'd', 'x', 'y', 'z', ''],
                                        self.addPoint, 2, 0, 1, 1,
                                        color = QtCore.Qt.red, onColorChange=changeColor(self.pd.pointPen))

        self.vectorTable = self.addTable(['Start Point', 'End Point', 'dx', 'dy', 'dz', 'Magnitude', 'Measured Mag.', ''],
                                         self.addVector, 2, 1, 1, 1,
                                         color = QtCore.Qt.black, onColorChange=changeColor(self.pd.vectorPen))
        self.angleTable = self.addTable(['Vector 1', 'Vector 2', 'Angle', 'xz', 'xy', 'yz'], self.addAngle, 0, 2, 1, 1)


        # Connect point and vector table changes to the PhotoDisplayer and DepthProvider.
        self.pointTable.onChange.connect(self.pd.update)
        self.pointTable.itemSelectionChanged.connect(self.pd.update)
        self.vectorTable.onChange.connect(self.pd.update)

        # Display is turned off until 2 images are uploaded.
        self.toggleTableEdits()

        # Button to tune hyperparameters.
        # self.buttonTuneParameters = QtWidgets.QPushButton("Tune Hyperparameters", self.centralwidget)
        # # TODO: setGeometry
        # self.buttonTuneParameters.clicked.connect(self.tuneParameters)

        # Set image properties of depthProvider.
        self.depthProvider.imageChanged.connect(self.setImage)
        self.depthProvider.imageScaled.connect(self.scalePoints)

        self.centralwidget.setLayout(self.layout)

    # Toggles table editing on or off.
    @QtCore.pyqtSlot()
    def toggleTableEdits(self):
        # Depending on current selection behavior, set to a different selection behavior and mode
        turned_on = False
        if (self.pointTable.editTriggers() == QtWidgets.QAbstractItemView.DoubleClicked):
            self.pointTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.vectorTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.angleTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        else:
            turned_on = True
            self.pointTable.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
            self.vectorTable.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
            self.angleTable.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        #print("Toggled Edits", turned_on)

    # Load depthProvider images into the PhotoDisplayer.
    @QtCore.pyqtSlot()
    def setImage(self):
        # Only if there were already two images.
        if self.imagePath[0] is not None and self.imagePath[1] is not None:
            # Reset the tables.
            self.pointTable.clearTable()
            self.vectorTable.clearTable()
            self.angleTable.clearTable()

            self.pointIdx = 0
            self.vectorIdx = 0
            self.angleIdx = 0

        # But depthProvider image into the PhotoDisplayer.
        self.pd.setNewPixmap(self.depthProvider.current_pixmap())
        self.pdContainer.fitToWindow()

    # Scales every point in the pointTable.
    @QtCore.pyqtSlot(float, float)
    def scalePoints(self, sx, sy):
        for name, point in self.pointTable:
            point.u *= sx
            point.v *= sy

    # Adds point if drawing is enabled.
    @QtCore.pyqtSlot()
    def addPoint(self):
        if self.pd.drawStuff:
            self.addPointAtPixel()

    # Adds point to pointTable.
    def addPointAtPixel(self, u = 0, v = 0):
        self.pointTable[createLabel(self.pointIdx)] = Point(self.depthProvider, u, v)
        self.pointIdx += 1

    # Adds vector to vectorTable.
    @QtCore.pyqtSlot()
    def addVector(self):
        if self.pd.drawStuff:
            # Don't add if vector already exists.
            selected = sorted(list(set(self.pointTable.row_name(x.row()) for x in self.pointTable.selectedItems())))
            for k, v in self.vectorTable:
                if sorted([v.s.name, v.t.name]) == selected:
                    return

            # Add vector to the table if two points were selected.
            if len(selected) == 2:
                vec = Vector(self.pointTable[selected[0]], self.pointTable[selected[1]])
                self.vectorTable[createLabel(self.vectorIdx)] = vec
                self.vectorIdx += 1

                vec.sourceChanged.connect(self.depthProvider.calibrate)


    # Adds angle to angleTable.
    @QtCore.pyqtSlot()
    def addAngle(self):
        if self.pd.drawStuff:
            # Don't add if angle already exists.
            selected = sorted(list(set(self.vectorTable.row_name(x.row()) for x in self.vectorTable.selectedItems())))
            for k, v in self.angleTable:
                if sorted([v.a.name, v.b.name]) == selected:
                    return

            # Add angle to teh table if two points were selected.
            if len(selected) == 2:
                ang = Angle(self.vectorTable[selected[0]], self.vectorTable[selected[1]])
                self.angleTable[createLabel(self.angleIdx)] = ang
                self.angleIdx += 1

    # Set up menu bar.
    def setupMenu(self, MainWindow):
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

        # Creates action to execute a function.
        def create_action(name, slot, desc = None, shortcut = None):
            action = QtWidgets.QAction(name, MainWindow)
            action.triggered.connect(slot)

            if desc:
                action.setStatusTip(desc)

            if shortcut:
                action.setShortcut(shortcut)

            return action

        # Creates all the actions for the menu bar.
        self.actionZoomIn = create_action("Zoom In 25%", self.pdContainer.zoomIn, "Zoom in on the image", "Ctrl+=")
        self.actionZoomOut = create_action("Zoom Out 25%", self.pdContainer.zoomOut, "Zoom out on the image", "Ctrl+-")
        self.actionZoomReset = create_action("Reset Zoom", self.pdContainer.resetZoom, "Restore Image to Normal Size", "Ctrl+r")
        self.actionLoadData = create_action("Load Data", self.loadGUIFromFile, "Load Data from SDFDATA File")
        self.actionExportData = create_action("Export Data", self.saveGUIToFile, "Exports the data", "Ctrl+S")
        self.actionUploadLeft = create_action("Upload Left", self.uploadImage(0), "Upload left half of a stereogram pair")
        self.actionUploadRight = create_action("Upload Right", self.uploadImage(1), "Upload right half of a stereogram pair")
        self.actionShowVectors = create_action("Toggle Vector Display", self.pd.toggleDraw)
        self.actionShowLeftImage = create_action("Show Left Image", lambda: self.displayImage(0))
        self.actionShowRightImage = create_action("Show Right Image", lambda: self.displayImage(1))
        self.actionShowInterpolatedImage = create_action("Show Interpolated Image", lambda: self.displayImage(2))
        self.actionShowDisparityMapImage = create_action("Show Disparity", lambda: self.displayImage(3))

        def add_actions_to_menu(menu, actions):
            for action in actions:
                menu.addAction(action)

        # Add actions to menus.
        add_actions_to_menu(self.menuFile, [self.actionLoadData, self.actionExportData])
        add_actions_to_menu(self.menuUploadImages, [self.actionUploadLeft, self.actionUploadRight])
        #add_actions_to_menu(self.menuToggleDisplayOptions, [self.actionShowVectors, self.actionShowLeftImage, self.actionShowRightImage, self.actionShowDisparityMapImage])
        add_actions_to_menu(self.menuZoomOptions, [self.actionZoomIn, self.actionZoomOut, self.actionZoomReset])

        # Interpolated image feature not implemented but here is how it would be added
        add_actions_to_menu(self.menuToggleDisplayOptions, [self.actionShowVectors, self.actionShowLeftImage, self.actionShowRightImage, self.actionShowInterpolatedImage, self.actionShowDisparityMapImage])

        # Add menus to menu bar.
        self.menubar.addMenu(self.menuFile)
        self.menubar.addMenu(self.menuUploadImages)
        self.menubar.addMenu(self.menuToggleDisplayOptions)
        self.menubar.addMenu(self.menuZoomOptions)

    # Upload image to the GUI.
    def uploadImage(self, idx):
        def f():
            desc = "Image File (*.jpeg *.jpg *.png *.gif *.tif *.tiff)"

            directory = self.lastDir if self.lastDir else os.getcwd()
            name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select an image file", directory, desc, desc)

            # Don't update if they didn't select an image
            # Probably also don't want to update if they select the same image
            if name:
                self.lastDir = os.path.dirname(name)
                self.imagePath[idx] = name
                self.depthProvider.set_image(idx, name)

                # Toggle display after both uploaded and depth calculated.
                if not(self.pd.drawStuff) and self.imagePath[1 - idx] is not None:
                    self.pd.toggleDraw()

                self.update()

        return f

    # Displays image in the depthProvider.
    def displayImage(self, selection):
        self.depthProvider.show(selection)

    def tuneParameters(self):
        dialog = editParametersDialog(self.pd)
        dialog.exec()

    def editParameters(self):
        dialog = parameterDialog()
        dialog.exec()

    # Write to a file
    # Can't pickle UI_MainWindow need to figure out how to do that
    # Probably best to use QDatastream instead
    def saveGUIToFile(self):
        fname = "SDFDATA File (*.SDFDATA)"
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Select Directory To Save To", os.getcwd(), fname, fname)

        objectToSave = {
            'point': {
                'idx': self.pointIdx,
                'table': self.pointTable.serialize(lambda p: p.serialize())
            },

            'vector': {
                'idx': self.vectorIdx,
                'table': self.vectorTable.serialize(lambda v: v.serialize())
            },

            'angle': {
                'idx': self.angleIdx,
                'table': self.angleTable.serialize(lambda a: a.serialize())
            },

            'images': self.depthProvider.get_images(),

            'disparity': self.depthProvider.get_disparity(),

            'colors': {
                'point': self.pd.pointPen.color(),
                'vector': self.pd.vectorPen.color()
            },

            'camera_params': {
                'fov': self.depthProvider.get_fov(),
                'baseline': self.depthProvider.get_baseline()
            }
        }

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
                state = pickle.load(handle)

                if 'camera_params' not in state.keys():
                    state['camera_params'] = {
                        'fov': 30 * math.pi / 180,
                        'baseline': 1
                    }

                # Load image path data
                self.depthProvider.reset(state['camera_params']['fov'],
                                         state['camera_params']['baseline'])

                for idx, img in enumerate(state['images']):
                    self.depthProvider.set_image(idx, img, calculate=False)
                self.depthProvider.set_disparity(state['disparity'])
                self.depthProvider.update_images_from_disparity()

                if self.depthProvider.should_calculate():
                    self.depthProvider.calculate()

                self.pd.toggleDraw(True)

                # Load point and vector data
                self.pointTable.deserialize(state['point']['table'], lambda v: Point(self.depthProvider, v[0], v[1]))
                self.pointIdx = state['point']['idx']

                self.vectorTable.deserialize(state['vector']['table'], lambda v: Vector(self.pointTable[v[0]], self.pointTable[v[1]]))
                self.vectorIdx = state['vector']['idx']

                for name, vec in self.vectorTable:
                    vec.sourceChanged.connect(self.depthProvider.calibrate)

                self.angleTable.deserialize(state['angle']['table'], lambda v: Angle(self.vectorTable[v[0]], self.vectorTable[v[1]]))
                self.angleIdx = state['angle']['idx']

                # Load pen colors
                # TODO: adjust color selector
                self.pd.pointPen.setColor(state['colors']['point'])
                self.pd.vectorPen.setColor(state['colors']['vector'])

                self.pd.update()
            return None
        else:
            return None


if __name__ == "__main__":
    import sys
    import math
    import numpy as np

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.setupMenu(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
