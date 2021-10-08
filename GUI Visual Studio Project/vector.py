import math
import numpy as np

class Vector(object):

    # This initialization gives a value equivalent to translating p1 to the origin and then translating p2 by the same amount
    def __init__(self, p1, p2):
        self.name = p1.name + p2.name
        self.realVector = np.subtract(p2.getRealCoordinates(),p1.getRealCoordinates())
        self.pixelVector = np.subtract(p2.getPixelCoordinates(),p1.getPixelCoordinates())

    def __str__(self):
        return "Point {0}:\nReal Coordinates: {1}\t Pixel Coordinates: {2}".format(self.name, self.getRealCoordinates(), self.getPixelCoordinates())

    def getRealCoordinates(self):
        return self.realVector

    def getPixelCoordinates(self):
        return self.pixelVector





