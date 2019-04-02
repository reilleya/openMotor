from .. import fmmGrain
from ..properties import *
from .. import simAlert, simAlertLevel, simAlertType

import numpy as np

class cGrain(fmmGrain):
    geomName = 'C Grain'
    def __init__(self):
        super().__init__()
        self.props['slotWidth'] = floatProperty('Slot width', 'm', 0, 1)
        self.props['slotOffset'] = floatProperty('Slot offset', 'm', -1, 1)

        self.props['slotOffset'].setValue(0)

    def generateCoreMap(self):
        slotWidth = self.normalize(self.props['slotWidth'].getValue())
        slotOffset = self.normalize(self.props['slotOffset'].getValue())

        self.coreMap[np.logical_and(np.abs(self.Y)< slotWidth/2, self.X > slotOffset)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if self.props['slotOffset'].getValue() > self.props['diameter'].getValue() / 2:
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Slot offset should be less than grain radius'))
        if self.props['slotOffset'].getValue() < -self.props['diameter'].getValue() / 2:
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Slot offset should be greater than negative grain radius'))

        if self.props['slotWidth'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Slot width must not be 0'))
        if self.props['slotWidth'].getValue() > self.props['diameter'].getValue():
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Slot width should not be greater than grain diameter'))

        return errors
