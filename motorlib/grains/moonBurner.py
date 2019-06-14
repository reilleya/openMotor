"""Moon burning grain submodule"""

from ..grain import FmmGrain
from ..properties import FloatProperty
from ..simResult import SimAlert, SimAlertLevel, SimAlertType

class MoonBurner(FmmGrain):
    """A moonburner is very similar to a BATES grain except the core is off center by a specified distance."""
    geomName = 'Moon Burner'
    def __init__(self):
        super().__init__()
        self.props['coreOffset'] = FloatProperty('Core offset', 'm', 0, 1)
        self.props['coreDiameter'] = FloatProperty('Core diameter', 'm', 0, 1)

    def generateCoreMap(self):
        coreRadius = self.normalize(self.props['coreDiameter'].getValue()) / 2
        coreOffset = self.normalize(self.props['coreOffset'].getValue())

        # Open up core
        self.coreMap[(self.mapX - coreOffset)**2 + self.mapY**2 < coreRadius**2] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        out = 'Length: ' + self.props['length'].dispFormat(lengthUnit)
        out += ', Core: ' + self.props['coreDiameter'].dispFormat(lengthUnit)
        return out

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['coreDiameter'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self.props['coreDiameter'].getValue() >= self.props['diameter'].getValue():
            aText = 'Core diameter must be less than or equal to grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))

        if self.props['coreOffset'].getValue() * 2 > self.props['diameter'].getValue():
            aText = 'Core offset should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
