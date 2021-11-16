import math
import numpy as np

class Vector(object):

    # This initialization gives a value equivalent to translating p1 to the origin and then translating p2 by the same amount
    def __init__(self, p1, p2, name=""):
        self.name = p1.name + "-" + p2.name
        if name != "":
            self.name = name
        self.point1Ref = p1
        self.point2Ref = p2

        self.update()

    def __str__(self):
        return "Point {0}:\nReal Coordinates: {1}\t Pixel Coordinates: {2}".format(self.name, self.getRealCoordinates(), self.getPixelCoordinates())

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

    def getReferencePoints(self):
        return [self.point1Ref, self.point2Ref]

    def update(self):
        self.realCoordinates = np.subtract(self.point2Ref.getRealCoordinates(),self.point1Ref.getRealCoordinates())
        self.pixelCoordinates = np.subtract(self.point2Ref.getPixelCoordinates(),self.point1Ref.getPixelCoordinates())





