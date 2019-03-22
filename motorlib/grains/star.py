from .. import perforatedGrain
from ..properties import *
from .. import simAlert, simAlertLevel, simAlertType

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

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['numPoints'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Star grain has 0 points'))

        if self.props['pointLength'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Point length must not be 0'))
        if self.props['pointLength'].getValue() * 2 > self.props['diameter'].getValue():
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Point length should be less than or equal to grain radius'))
        
        if self.props['pointWidth'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Point width must not be 0'))

        return errors
