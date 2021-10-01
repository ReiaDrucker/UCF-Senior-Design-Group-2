import math

class Point(object):

    def __init__(self, name, x, y, z, length, width):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.length = length
        self.width = width

    def __str__(self):
        return "Point {0}:\nReal Coordinates: ({1}, {2}, {3})\t Pixel Coordinates: ({4}, {5})".format(self.name, self.x, self.y, self.z, self.length, self.width)

    # Used to get the (x, y, z) coordinates in array form
    def getRealCoordinates(self):
        return [self.x, self.y, self.z]

    # Used to get the (length, witdth) coordinates in array form
    def getPixelCoordinates(self):
        return [self.length, self.width]

    # Calculates magnitude of length from (0,0,0) to current point.
    def getMagnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)







