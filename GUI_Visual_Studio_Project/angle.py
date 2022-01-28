import math
import numpy as np

class Angle(object):

    # Initializes angle object.
    def __init__(self, v1, v2, name=""):
        self.name = v1.name + "/" + v2.name
        if name != "":
            self.name = name
        self.vector1Ref = v1
        self.vector2Ref = v2
        self.value = math.degrees(Angle.calculateAngle(v1, v2))

    def calculateAngle(v1, v2):
        # x1 = v1.getReferencePoints()[0].getPixelCoordinates()[0]
        # x2 = v2.getReferencePoints()[0].getPixelCoordinates()[0]
        # x3 = v1.getReferencePoints()[1].getPixelCoordinates()[0]
        # x4 = v2.getReferencePoints()[1].getPixelCoordinates()[0]

        # y1 = v1.getReferencePoints()[0].getPixelCoordinates()[1]
        # y2 = v2.getReferencePoints()[0].getPixelCoordinates()[1]
        # y3 = v1.getReferencePoints()[1].getPixelCoordinates()[1]
        # y4 = v2.getReferencePoints()[1].getPixelCoordinates()[1]

        uv1 = v1.getPixelCoordinates() / np.linalg.norm(v1.getPixelCoordinates())
        uv2 = v2.getPixelCoordinates() / np.linalg.norm(v2.getPixelCoordinates())
        return np.arccos(np.dot(uv1, uv2))

    def getAngleStr(self):
        return "{:.2f}".format(self.value)

    def getComboStr(self):
        return self.name + ": " + self.getAngleStr()