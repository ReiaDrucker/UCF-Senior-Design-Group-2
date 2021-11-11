import math
import numpy as np

class Vector(object):

    # This initialization gives a value equivalent to translating p1 to the origin and then translating p2 by the same amount
    def __init__(self, p1, p2, name=""):
        self.name = p1.name + "-" + p2.name
        if name != "":
            self.name = name
        self.realCoordinates = np.subtract(p2.getRealCoordinates(),p1.getRealCoordinates())
        self.pixelCoordinates = np.subtract(p2.getPixelCoordinates(),p1.getPixelCoordinates())
        self.point1Ref = p1
        self.point2Ref = p2

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

    def getReferencePoints(self):
        return [self.point1Ref, self.point2Ref]





