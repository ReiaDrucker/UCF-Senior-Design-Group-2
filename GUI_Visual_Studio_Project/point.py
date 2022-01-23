import math
import numpy as np

class Point(object):

    def __init__(self, name, x, y, z, length, width):
        self.name = name
        self.realCoordinates = np.array([x,y,z])
        self.pixelCoordinates = np.array([length, width])

    def __str__(self):
        return "Point {0}:\nReal Coordinates: {1}\t Pixel Coordinates: {2}".format(self.name, self.getRealCoordinates(), self.getPixelCoordinates())

    def getRealCoordinates(self):
        return self.realCoordinates

    def getRealCoordinatesStr(self):
        return "({:.2f}, {:.2f}, {:.2f})".format(self.realCoordinates[0], self.realCoordinates[1], self.realCoordinates[2])

    def getPixelCoordinates(self):
        return self.pixelCoordinates

    def getPixelCoordinatesStr(self):
        return "({:.2f}, {:.2f})".format(self.pixelCoordinates[0], self.pixelCoordinates[1])

    def getComboStr(self):
        return self.name + ": " + self.getPixelCoordinatesStr() + "; " + self.getRealCoordinatesStr()



