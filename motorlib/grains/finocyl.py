from ..grain import FmmGrain
from ..properties import *
from ..simResult import SimAlert, SimAlertLevel, SimAlertType

import numpy as np

class Finocyl(FmmGrain):
    geomName = 'Finocyl'
    def __init__(self):
        super().__init__()
        self.props['numFins'] = IntProperty('Number of fins', '', 0, 64)
        self.props['finWidth'] = FloatProperty('Fin width', 'm', 0, 1)
        self.props['finLength'] = FloatProperty('Fin length', 'm', 0, 1)
        self.props['coreDiameter'] = FloatProperty('Core diameter', 'm', 0, 1)

    def generateCoreMap(self):
        coreRadius = self.normalize(self.props['coreDiameter'].getValue()) / 2
        numFins = self.props['numFins'].getValue()
        finWidth = self.normalize(self.props['finWidth'].getValue())
        finLength = self.normalize(self.props['finLength'].getValue()) + coreRadius # The user enters the length that the fin protrudes from the core, so we add the radius on

        # Open up core
        self.coreMap[self.mapX**2 + self.mapY**2 < coreRadius**2] = 0

        # Add fins
        for i in range(0, numFins):
            th = 2 * np.pi / numFins * i
            # Initialize a vector pointing along the fin
            a = np.cos(th)
            b = np.sin(th)
            # Select all points within half the width of the vector
            vect = abs(a*self.mapX + b*self.mapY) < finWidth / 2
            # Set up two perpendicular vectors to cap off the ends
            near = (b * self.mapX) - (a * self.mapY) > 0 # Inside of the core
            far = (b * self.mapX) - (a * self.mapY) < finLength # At the casting tube end of the vector
            ends = np.logical_and(far, near)
            # Open up the fin
            self.coreMap[np.logical_and(vect, ends)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit) + ', Core: ' + self.props['coreDiameter'].dispFormat(lengthUnit) + ', Fins: ' + str(self.props['numFins'].getValue())

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['coreDiameter'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self.props['coreDiameter'].getValue() >= self.props['diameter'].getValue():
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must be less than or equal to grain diameter'))

        if self.props['finLength'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Fin length must not be 0'))
        if self.props['finLength'].getValue() * 2 > self.props['diameter'].getValue():
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Fin length should be less than or equal to grain radius'))
        if self.props['coreDiameter'].getValue() + (2 * self.props['finLength'].getValue()) > self.props['diameter'].getValue():
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Core radius plus fin length should be less than or equal to grain radius'))

        if self.props['finWidth'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Fin width must not be 0'))
        if self.props['numFins'].getValue() > 1:
            if 2 * (self.props['coreDiameter'].getValue() / 2 + self.props['finLength'].getValue()) * np.tan(np.pi / self.props['numFins'].getValue()) < self.props['finWidth'].getValue():
                errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Fin tips intersect'))

        return errors
