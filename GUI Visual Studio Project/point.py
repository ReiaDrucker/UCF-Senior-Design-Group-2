import math
import numpy as np

class Point(object):

    def __init__(self, name, length, width, real = None):
        self.name = name
        self.pixelCoordinates = np.array([length, width])

        if real is not None:
            self.updateReal(real)
        else:
            self.realCoordinates = np.array([0, 0, 0])

    def __str__(self):
        return "Point {0}:\nReal Coordinates: {1}\t Pixel Coordinates: {2}".format(self.name, self.getRealCoordinates(), self.getPixelCoordinates())

    def updateReal(self, real):
        self.realCoordinates = real[self.pixelCoordinates[1],self.pixelCoordinates[0],:]

    def getRealCoordinates(self):
        return self.realCoordinates

    def getRealCoordinatesStr(self):
        return "(" + str(self.realCoordinates[0]) + ", " + str(self.realCoordinates[1]) + ", " + str(self.realCoordinates[2]) + ")"

    def getPixelCoordinates(self):
        return self.pixelCoordinates

    def getPixelCoordinatesStr(self):
        return "(" + str(self.pixelCoordinates[0]) + ", " + str(self.pixelCoordinates[1]) + ")"

    def getComboStr(self):
        return self.name + ": " + self.getPixelCoordinatesStr() + "; " + self.getRealCoordinatesStr()



