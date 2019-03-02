from .. import perforatedGrain
from ..properties import *

import numpy as np

class cGrain(perforatedGrain):
    geomName = 'C Grain'
    def __init__(self):
        super().__init__()
        self.props['slotWidth'] = floatProperty('Slot width', 'm', 0, 1)
        self.props['slotOffset'] = floatProperty('Slot offset', 'm', 0, 1)

    def generateCoreMap(self):
        slotWidth = self.normalize(self.props['slotWidth'].getValue())
        slotOffset = self.normalize(self.props['slotOffset'].getValue())

        self.coreMap[np.logical_and(np.abs(self.Y)< slotWidth/2, self.X > slotOffset)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit)
