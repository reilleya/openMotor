from .. import perforatedGrain
from ..properties import *
from .. import simAlert, simAlertLevel, simAlertType

import numpy as np

class xCore(perforatedGrain):
    geomName = 'X Core'
    def __init__(self):
        super().__init__()
        self.props['slotWidth'] = floatProperty('Slot width', 'm', 0, 1)
        self.props['slotLength'] = floatProperty('Slot length', 'm', 0, 1)

    def generateCoreMap(self):
        slotWidth = self.normalize(self.props['slotWidth'].getValue())
        slotLength = self.normalize(self.props['slotLength'].getValue())

        self.coreMap[np.logical_and(np.abs(self.Y) < slotWidth/2, np.abs(self.X) < slotLength)] = 0
        self.coreMap[np.logical_and(np.abs(self.X) < slotWidth/2, np.abs(self.Y) < slotLength)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit) + ', Slots: ' + self.props['slotWidth'].dispFormat(lengthUnit) + ' by ' + self.props['slotLength'].dispFormat(lengthUnit)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['slotWidth'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Slot width must not be 0'))
        if self.props['slotWidth'].getValue() > self.props['diameter'].getValue():
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Slot width should be less than or equal to grain diameter'))

        if self.props['slotLength'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Slot length must not be 0'))
        if self.props['slotLength'].getValue() * 2 > self.props['diameter'].getValue():
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Slot length should be less than or equal to grain radius'))
          
        return errors
