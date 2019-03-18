from .. import perforatedGrain
from ..properties import *

import numpy as np

class starGrain(perforatedGrain):
    geomName = 'Star Grain'
    def __init__(self):
        super().__init__()
        self.props['numPoints'] = intProperty('Number of points', '', 0, 64)
        self.props['pointLength'] = floatProperty('Point length', 'm', 0, 1)
        self.props['pointWidth'] = floatProperty('Point base width', 'm', 0, 1)

    def generateCoreMap(self):
        numPoints = self.props['numPoints'].getValue()
        pointWidth = self.normalize(self.props['pointWidth'].getValue())
        pointLength = self.normalize(self.props['pointLength'].getValue())

        for i in range(0, numPoints):
            th = 2 * np.pi / numPoints * i
            a = np.cos(th)
            b = np.sin(th)

            vect = abs(a * self.X + b * self.Y) < pointWidth / 2 * (1 - (((self.X ** 2 + self.Y ** 2) ** 0.5) / pointLength))
            near = b*self.X - a*self.Y > -0.025
            self.coreMap[np.logical_and(vect, near)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit) + ', Points: ' + str(self.props['numPoints'].getValue())
