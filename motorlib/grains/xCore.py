"""X Core grain submodule"""

import numpy as np

from ..enums.simAlertLevel import SimAlertLevel
from ..enums.simAlertType import SimAlertType
from ..grain import FmmGrain
from ..properties import FloatProperty
from ..simResult import SimAlert

class XCore(FmmGrain):
    """An X Core grain has a core shaped like a plus sign or an X."""
    geomName = 'X Core'
    def __init__(self):
        super().__init__()
        self.props['slotWidth'] = FloatProperty('Slot width', 'm', 0, 1)
        self.props['slotLength'] = FloatProperty('Slot length', 'm', 0, 1)

    def generateCoreMap(self):
        slotWidth = self.normalize(self.props['slotWidth'].getValue())
        slotLength = self.normalize(self.props['slotLength'].getValue())

        self.coreMap[np.logical_and(np.abs(self.mapY) < slotWidth/2, np.abs(self.mapX) < slotLength)] = 0
        self.coreMap[np.logical_and(np.abs(self.mapX) < slotWidth/2, np.abs(self.mapY) < slotLength)] = 0

    def getDetailsString(self, lengthUnit='m'):
        return 'Length: {}, Slots: {} by {}'.format(self.props['length'].dispFormat(lengthUnit),
                                                    self.props['slotWidth'].dispFormat(lengthUnit),
                                                    self.props['slotLength'].dispFormat(lengthUnit))

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['slotWidth'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Slot width must not be 0'))
        if self.props['slotWidth'].getValue() > self.props['diameter'].getValue():
            aText = 'Slot width should be less than or equal to grain diameter'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self.props['slotLength'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Slot length must not be 0'))
        if self.props['slotLength'].getValue() * 2 > self.props['diameter'].getValue():
            aText = 'Slot length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
