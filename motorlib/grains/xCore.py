from .. import perforatedGrain
from ..properties import *

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
