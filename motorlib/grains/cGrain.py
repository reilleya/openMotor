"""C Grain submodule"""

import numpy as np

from ..grain import FmmGrain
from ..properties import FloatProperty
from ..simResult import SimAlert, SimAlertLevel, SimAlertType

class CGrain(FmmGrain):
    """Defines a C grain, which is a cylindrical grain with a single slot taken out. The slot is a rectangular section
    with a certain width that starts at the casting tube and protrudes towards the center of the grain, stopping a
    specified offset away."""
    geomName = 'C Grain'
    def __init__(self):
        super().__init__()
        self.props['slotWidth'] = FloatProperty('Slot width', 'm', 0, 1)
        self.props['slotOffset'] = FloatProperty('Slot offset', 'm', -1, 1)

        self.props['slotOffset'].setValue(0)

    def generateCoreMap(self):
        slotWidth = self.normalize(self.props['slotWidth'].getValue())
        slotOffset = self.normalize(self.props['slotOffset'].getValue())

        self.coreMap[np.logical_and(np.abs(self.mapY) < slotWidth/2, self.mapX > slotOffset)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if self.props['slotOffset'].getValue() > self.props['diameter'].getValue() / 2:
            aText = 'Slot offset should be less than grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))
        if self.props['slotOffset'].getValue() < -self.props['diameter'].getValue() / 2:
            aText = 'Slot offset should be greater than negative grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self.props['slotWidth'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Slot width must not be 0'))
        if self.props['slotWidth'].getValue() > self.props['diameter'].getValue():
            aText = 'Slot width should not be greater than grain diameter'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
