"""BATES submodule"""

import numpy as np
import skfmm
from skimage import measure
from math import atan, cos, sin

from ..grain import Grain
from .. import geometry
from ..simResult import SimAlert, SimAlertLevel, SimAlertType
from ..properties import FloatProperty, EnumProperty

class ConicalGrain(Grain):
    """A conical grain is similar to a BATES grain except it has different core diameters at each end."""
    geomName = "Conical"
    def __init__(self):
        super().__init__()
        self.props['aftCoreDiameter'] = FloatProperty('Aft Core Diameter', 'm', 0, 1)
        self.props['forwardCoreDiameter'] = FloatProperty('Forward Core Diameter', 'm', 0, 1)
        self.props['inhibitedEnds'] = EnumProperty('Inhibited ends', ['Neither', 'Top', 'Bottom', 'Both'])

    def getFrustrumInfo(self, regDist):
        grainDiam = self.props['diameter'].getValue()
        aftDiam = self.props['aftCoreDiameter'].getValue()
        forwardDiam = self.props['forwardCoreDiameter'].getValue()
        length = self.props['length'].getValue()

        angle = atan((aftDiam - forwardDiam) / (2 * length))
        regAftDiam = aftDiam + (regDist * 2 * cos(angle))
        regForwardDiam = forwardDiam + (regDist * 2 * cos(angle))

        exposedFaces = 0
        inhibitedEnds = self.props['inhibitedEnds'].getValue()
        if inhibitedEnds == 'Neither':
            exposedFaces = 2
        elif inhibitedEnds in ['Top', 'Bottom']:
            exposedFaces = 1

        if regAftDiam >= grainDiam:
            #print('Case 1')
            majorDiameter = grainDiam
            minorDiameter = regForwardDiam
            effectiveReg = (regAftDiam - grainDiam) / 2
            length -= (effectiveReg / sin(angle))
            #length -= (grainDiam - aftDiam / 2) * exposedFaces
            #if self.props['inhibitedEnds'].getValue() in ['Neither', 'Bottom']:
            #    length -= regDist
        else:
            #print('Case 2')
            majorDiameter = regAftDiam
            minorDiameter = regForwardDiam
            length -= exposedFaces * regDist

        # For now we can assume the faces are inhibited
        return majorDiameter, minorDiameter, length

    def getSurfaceAreaAtRegression(self, regDist):
        """Returns the surface area of the grain after it has regressed a linear distance of 'regDist'"""
        majorDiameter, minorDiameter, length = self.getFrustrumInfo(regDist)
        majorRadius = majorDiameter / 2
        minorRadius = minorDiameter / 2
        # TODO: Move to a geometry function and test it
        surf = 3.1415926 * (majorRadius + minorRadius) * ((majorRadius - minorRadius) ** 2 + length ** 2) ** 0.5

        fullFaceArea = geometry.circleArea(self.props['diameter'].getValue())
        if self.props['inhibitedEnds'].getValue() in ['Neither', 'Bottom']:
            surf += fullFaceArea - geometry.circleArea(minorDiameter)
        if self.props['inhibitedEnds'].getValue() in ['Neither', 'Top']:
            surf += fullFaceArea - geometry.circleArea(majorDiameter)
        #surf += 2 * geometry.circleArea(self.props['diameter'].getValue())
        #surf -= geometry.circleArea(majorDiameter) + geometry.circleArea(minorDiameter)
        #print('Surface: {}'.format(surf))
        return surf

    def getVolumeAtRegression(self, regDist):
        """Returns the volume of propellant in the grain after it has regressed a linear distance 'regDist'"""
        majorDiameter, minorDiameter, length = self.getFrustrumInfo(regDist)
        majorRadius = majorDiameter / 2
        minorRadius = minorDiameter / 2
        frustrumVolume = 3.1415926 * (length / 3) * (majorRadius ** 2 + minorRadius * minorRadius + minorRadius ** 2)
        outerVolume = geometry.cylinderVolume(self.props['diameter'].getValue(), length)
        return outerVolume - frustrumVolume

    def getWebLeft(self, regDist):
        """Returns the shortest distance the grain has to regress to burn out"""
        majorDiameter, minorDiameter, length = self.getFrustrumInfo(regDist)
        return (self.props['diameter'].getValue() - minorDiameter) / 2

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flux at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""
        return 0

    def getPeakMassFlux(self, massIn, dTime, regDist, dRegDist, density):
        """Uses the grain's mass flux method to return the max. Need to define this here because I'm not sure what
        it will look like"""
        return 0

    def getEndPositions(self, regDist):
        """Returns the positions of the grain ends relative to the original (unburned) grain top"""
        return 0

    def getPortArea(self, regDist):
        """Returns the area of the grain's port when it has regressed a distance of 'regDist'"""
        return 0

    def getDetailsString(self, lengthUnit='m'):
        """Returns a short string describing the grain, formatted using the units that is passed in"""
        return 'Length: {}'.format(self.props['length'].dispFormat(lengthUnit))

    def simulationSetup(self, config):
        """Do anything needed to prepare this grain for simulation"""
        return None

    def getGeometryErrors(self):
        """Returns a list of simAlerts that detail any issues with the geometry of the grain. Errors should be
        used for any condition that prevents simulation of the grain, while warnings can be used to notify the
        user of possible non-fatal mistakes in their entered numbers. Subclasses should still call the superclass
        method, as it performs checks that still apply to its subclasses."""
        errors = []
        if self.props['diameter'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Diameter must not be 0'))
        if self.props['length'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Length must not be 0'))
        return errors
