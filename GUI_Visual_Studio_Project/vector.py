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
        return "({:.2f}, {:.2f}, {:.2f})".format(self.realCoordinates[0], self.realCoordinates[1], self.realCoordinates[2])

    def getPixelCoordinates(self):
        return self.pixelCoordinates

    def getPixelCoordinatesStr(self):
        return "({:.2f}, {:.2f})".format(self.pixelCoordinates[0], self.pixelCoordinates[1])

    def getComboStr(self):
        return self.name + ": " + self.getPixelCoordinatesStr() + "; " + self.getRealCoordinatesStr()

    def getReferencePoints(self):
        return [self.point1Ref, self.point2Ref]