from .. import perforatedGrain
from ..properties import *

import numpy as np

class dGrain(perforatedGrain):
    geomName = 'D Grain'
    def __init__(self):
        super().__init__()
        self.props['slotOffset'] = floatProperty('Slot offset', 'm', 0, 1)

    def generateCoreMap(self):
        slotOffset = self.normalize(self.props['slotOffset'].getValue())

        self.coreMap[self.X > slotOffset] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Slot offset: ' + self.props['slotOffset'].dispFormat(lengthUnit)
