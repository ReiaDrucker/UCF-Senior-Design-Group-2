import math

class Vector(object):

    # This initialization gives a value equivalent to translating p1 to the origin and then translating p2 by the same amount
    def __init__(self, p1, p2):
        self.name = p1.name + p2.name
        self.x = p2.x-p1.x
        self.y = p2.y-p1.y
        self.z = p2.z-p1.z
        self.length = p2.length-p1.length
        self.width = p2.width-p1.width

    def __str__(self):
        return "Vector {0}:\nReal Coordinates: ({1}, {2}, {3})\t Pixel Coordinates: ({4}, {5})".format(self.name, self.x, self.y, self.z, self.length, self.width)

    # Used to get the (x, y, z) coordinates in array form
    def getRealCoordinates(self):
        return [self.x, self.y, self.z]

    def getRealMagnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def getRealDot(self, vec):
        return (self.x * vec.x) + (self.y * vec.y) + (self.z * vec.z)

    # Returns the angle in radians
    def getRealAngle(self, vec):
        return math.acos(self.getRealDot(vec) / (self.getRealMagnitude() * vec.getRealMagnitude()))

    # Used to get the (length, witdth) coordinates in array form
    def getPixelCoordinates(self):
        return [self.length, self.width]

    def getPixelMagnitude(self):
        return math.sqrt(self.length**2 + self.width**2)

    def getPixelDot(self, vec):
        return (self.length * vec.length) + (self.width * vec.width)

    # Returns the angle in radians
    def getPixelAngle(self, vec):
        return math.acos(self.getPixelDot(vec) / (self.getPixelMagnitude() * vec.getPixelMagnitude()))




