from ..grain import FmmGrain
from ..properties import *
from ..simResult import simAlert, simAlertLevel, simAlertType

import numpy as np

class DGrain(FmmGrain):
    geomName = 'D Grain'
    def __init__(self):
        super().__init__()
        self.props['slotOffset'] = floatProperty('Slot offset', 'm', -1, 1)

        self.props['slotOffset'].setValue(0)

    def generateCoreMap(self):
        slotOffset = self.normalize(self.props['slotOffset'].getValue())

        self.coreMap[self.mapX > slotOffset] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit) + ', Slot offset: ' + self.props['slotOffset'].dispFormat(lengthUnit)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if self.props['slotOffset'].getValue() > self.props['diameter'].getValue() / 2:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Core offset must not be greater than grain radius'))
        if self.props['slotOffset'].getValue() < -self.props['diameter'].getValue() / 2:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Core offset must be greater than negative grain radius'))

        return errors
