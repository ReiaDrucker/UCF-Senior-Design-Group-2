import math

class Vector(object):
    def __init__(self, p1, p2):
        self.name = p1.name + p2.name
        self.x = p1.x-p2.x
        self.y = p1.y-p2.y
        self.z = p1.z-p2.z
        self.length = p1.length-p2.length
        self.width = p1.width-p2.width

    def __str__(self):
        return "Vector {0}:\nReal Coordinates: ({1}, {2}, {3})\t Pixel Coordinates: ({4}, {5})".format(self.name, self.x, self.y, self.z, self.length, self.width)

    # Used to get the (x, y, z) coordinates in array form
    def getRealCoordinates(self):
        return [self.x, self.y, self.z]

    # Used to get the (length, witdth) coordinates in array form
    def getPixelCoordinates(self):
        return [self.length, self.width]

    def getMagnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)




