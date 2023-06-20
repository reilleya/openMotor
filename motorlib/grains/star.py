"""Star grain submodule"""

import numpy as np

from ..enums.simAlertLevel import SimAlertLevel
from ..enums.simAlertType import SimAlertType
from ..enums.unit import Unit
from ..grain import FmmGrain
from ..properties import IntProperty, FloatProperty
from ..simResult import SimAlert

class StarGrain(FmmGrain):
    """A star grain has a core shaped like a star."""
    geomName = 'Star Grain'
    def __init__(self):
        super().__init__()
        self.props['numPoints'] = IntProperty('Number of points', '', 0, 64)
        self.props['pointLength'] = FloatProperty('Point length', Unit.METER, 0, 1)
        self.props['pointWidth'] = FloatProperty('Point base width', Unit.METER, 0, 1)

    def generateCoreMap(self):
        numPoints = self.props['numPoints'].getValue()
        pointWidth = self.normalize(self.props['pointWidth'].getValue())
        pointLength = self.normalize(self.props['pointLength'].getValue())

        for i in range(0, numPoints):
            theta = 2 * np.pi / numPoints * i
            comp0 = np.cos(theta)
            comp1 = np.sin(theta)

            rect = abs(comp0 * self.mapX + comp1 * self.mapY)
            width = pointWidth / 2 * (1 - (((self.mapX ** 2 + self.mapY ** 2) ** 0.5) / pointLength))
            vect = rect < width
            near = comp1*self.mapX - comp0*self.mapY > -0.025
            self.coreMap[np.logical_and(vect, near)] = 0

    def getDetailsString(self, Unit=Unit.METER):
        return 'Length: {}, Points: {}'.format(self.props['length'].dispFormat(Unit),
                                               self.props['numPoints'].getValue())

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['numPoints'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Star grain has 0 points'))

        if self.props['pointLength'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Point length must not be 0'))
        if self.props['pointLength'].getValue() * 2 > self.props['diameter'].getValue():
            aText = 'Point length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self.props['pointWidth'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Point width must not be 0'))

        return errors
