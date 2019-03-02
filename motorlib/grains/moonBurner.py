from .. import perforatedGrain
from ..properties import *

import numpy as np

class moonBurner(perforatedGrain):
    geomName = 'Moon Burner'
    def __init__(self):
        super().__init__()
        self.props['coreOffset'] = floatProperty('Core Offset', 'm', 0, 1)
        self.props['coreDiameter'] = floatProperty('Core diameter', 'm', 0, 1)

    def generateCoreMap(self):
        coreRadius = self.normalize(self.props['coreDiameter'].getValue()) / 2
        coreOffset = self.normalize(self.props['coreOffset'].getValue())

        # Open up core
        self.coreMap[(self.X - coreOffset)**2 + self.Y**2 < coreRadius**2] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Core: ' + self.props['coreDiameter'].dispFormat(lengthUnit) + ', Offset: ' + self.props['coreOffset'].dispFormat(lengthUnit)
