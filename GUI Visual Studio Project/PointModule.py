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

    def getRealCoordinates()
        return [self.x, self.y, self.z]







