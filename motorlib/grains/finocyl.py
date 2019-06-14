"""Finocyl grain submodule"""

import numpy as np

from ..grain import FmmGrain
from ..properties import FloatProperty, IntProperty
from ..simResult import SimAlert, SimAlertLevel, SimAlertType

class Finocyl(FmmGrain):
    """A finocyl (fins on cylinder) grain has a circular core with a number of rectangular extensions that start at the
    circle's edge and protude along its normals."""
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
        # The user enters the length that the fin protrudes from the core, so we add the radius on
        finLength = self.normalize(self.props['finLength'].getValue()) + coreRadius

        # Open up core
        self.coreMap[self.mapX**2 + self.mapY**2 < coreRadius**2] = 0

        # Add fins
        for i in range(0, numFins):
            theta = 2 * np.pi / numFins * i
            # Initialize a vector pointing along the fin
            vect0 = np.cos(theta)
            vect1 = np.sin(theta)
            # Select all points within half the width of the vector
            vect = abs(vect0*self.mapX + vect1*self.mapY) < finWidth / 2
            # Set up two perpendicular vectors to cap off the ends
            near = (vect1 * self.mapX) - (vect0 * self.mapY) > 0 # Inside of the core
            far = (vect1 * self.mapX) - (vect0 * self.mapY) < finLength # At the casting tube end of the vector
            ends = np.logical_and(far, near)
            # Open up the fin
            self.coreMap[np.logical_and(vect, ends)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        out = 'Length: ' + self.props['length'].dispFormat(lengthUnit)
        out += ', Core: ' + self.props['coreDiameter'].dispFormat(lengthUnit)
        out += ', Fins: ' + str(self.props['numFins'].getValue())
        return out

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['coreDiameter'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self.props['coreDiameter'].getValue() >= self.props['diameter'].getValue():
            aText = 'Core diameter must be less than or equal to grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))

        if self.props['finLength'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Fin length must not be 0'))
        if self.props['finLength'].getValue() * 2 > self.props['diameter'].getValue():
            aText = 'Fin length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))
        coreWidth = self.props['coreDiameter'].getValue() + (2 * self.props['finLength'].getValue())
        if coreWidth > self.props['diameter'].getValue():
            aText = 'Core radius plus fin length should be less than or equal to grain radius'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        if self.props['finWidth'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Fin width must not be 0'))
        if self.props['numFins'].getValue() > 1:
            radius = self.props['coreDiameter'].getValue() / 2
            apothem = radius + self.props['finLength'].getValue()
            sideLength = 2 * apothem * np.tan(np.pi / self.props['numFins'].getValue())
            if sideLength < self.props['finWidth'].getValue():
                errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, 'Fin tips intersect'))

        return errors
