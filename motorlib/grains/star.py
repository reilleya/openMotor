from ..grain import FmmGrain
from ..properties import *
from ..simResult import SimAlert, SimAlertLevel, SimAlertType

import numpy as np

class StarGrain(FmmGrain):
    geomName = 'Star Grain'
    def __init__(self):
        super().__init__()
        self.props['numPoints'] = IntProperty('Number of points', '', 0, 64)
        self.props['pointLength'] = FloatProperty('Point length', 'm', 0, 1)
        self.props['pointWidth'] = FloatProperty('Point base width', 'm', 0, 1)

    def generateCoreMap(self):
        numPoints = self.props['numPoints'].getValue()
        pointWidth = self.normalize(self.props['pointWidth'].getValue())
        pointLength = self.normalize(self.props['pointLength'].getValue())

        for i in range(0, numPoints):
            th = 2 * np.pi / numPoints * i
            a = np.cos(th)
            b = np.sin(th)

            vect = abs(a * self.mapX + b * self.mapY) < pointWidth / 2 * (1 - (((self.mapX ** 2 + self.mapY ** 2) ** 0.5) / pointLength))
            near = b*self.mapX - a*self.mapY > -0.025
            self.coreMap[np.logical_and(vect, near)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit) + ', Points: ' + str(self.props['numPoints'].getValue())

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['numPoints'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Star grain has 0 points'))

        if self.props['pointLength'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Point length must not be 0'))
        if self.props['pointLength'].getValue() * 2 > self.props['diameter'].getValue():
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Point length should be less than or equal to grain radius'))
        
        if self.props['pointWidth'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Point width must not be 0'))

        return errors
