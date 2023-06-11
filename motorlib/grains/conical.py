"""BATES submodule"""

import numpy as np
import skfmm
from skimage import measure
from math import atan, cos, sin

from ..enums.inhibitedEnds import InhibitedEnds
from ..enums.simAlertLevel import SimAlertLevel
from ..enums.simAlertType import SimAlertType
from ..enums.units.lengthUnit import LengthUnit
from ..grain import Grain
from .. import geometry
from ..simResult import SimAlert
from ..properties import FloatProperty, EnumProperty

class ConicalGrain(Grain):
    """A conical grain is similar to a BATES grain except it has different core diameters at each end."""
    geomName = "Conical"
    def __init__(self):
        super().__init__()
        self.props['forwardCoreDiameter'] = FloatProperty('Forward Core Diameter', LengthUnit.METER, 0, 1)
        self.props['aftCoreDiameter'] = FloatProperty('Aft Core Diameter', LengthUnit.METER, 0, 1)
        self.props['inhibitedEnds'] = EnumProperty('Inhibited ends', [InhibitedEnds.BOTH])

    def isCoreInverted(self):
        """A simple helper that returns 'true' if the core's foward diameter is larger than its aft diameter"""
        return self.props['forwardCoreDiameter'].getValue() > self.props['aftCoreDiameter'].getValue()

    def getFrustumInfo(self, regDist):
        """Returns the dimensions of the grain's core at a given regression depth. The core is always a frustum and is
        returned as the aft diameter, forward diameter, and length"""
        grainDiameter = self.props['diameter'].getValue()
        aftDiameter = self.props['aftCoreDiameter'].getValue()
        forwardDiameter = self.props['forwardCoreDiameter'].getValue()
        grainLength = self.props['length'].getValue()

        exposedFaces = 0
        inhibitedEnds = self.props['inhibitedEnds'].getValue()
        if inhibitedEnds == InhibitedEnds.NEITHER:
            exposedFaces = 2
        elif inhibitedEnds in [InhibitedEnds.TOP, InhibitedEnds.BOTTOM]:
            exposedFaces = 1

        # These calculations are easiest if we work in terms of the core's "large end" and "small end"
        if self.isCoreInverted():
            coreMajorDiameter, coreMinorDiameter = forwardDiameter, aftDiameter
        else:
            coreMajorDiameter, coreMinorDiameter = aftDiameter, forwardDiameter

        # Calculate the half angle of the core. This is done with without accounting for regression because it doesn't
        # change with regression
        angle = atan((coreMajorDiameter - coreMinorDiameter) / (2 * grainLength))

        # Expand both core diameters by the radial component of the core's regression vector. This is allowed to expand
        # beyond the casting tube as that condition is checked in a later step
        regCoreMajorDiameter = coreMajorDiameter + (regDist * 2 * cos(angle))
        regCoreMinorDiameter = coreMinorDiameter + (regDist * 2 * cos(angle))

        # This is case where the larger core diameter has grown beyond the casting tube diameter. Once this happens,
        # the diameter of the large end of the core is clamped at the grain diameter and the length is changed to keep
        # the angle constant, which accounts for the regression of the grain at the major end.
        if regCoreMajorDiameter >= grainDiameter:
            majorFrustumDiameter = grainDiameter
            minorFrustumDiameter = regCoreMinorDiameter
            # How far past the grain diameter the major end has grown
            effectiveReg = (regCoreMajorDiameter - grainDiameter) / 2
            # Reduce the length of the frustum by the axial component of the regression vector
            grainLength -= (effectiveReg / sin(angle))
            # Account for the change in length due to face regression before the major end hit the casting tube
            grainLength -= exposedFaces * (grainDiameter - coreMajorDiameter) / 2
            # Don't double count face regression
            grainLength += exposedFaces * effectiveReg

        # If the large end of the core hasn't reached the casting tube, we know that the small end hasn't either. In
        # this case we just return the current core diameters, and a length calculated from the inhibitor configuration
        else:
            majorFrustumDiameter = regCoreMajorDiameter
            minorFrustumDiameter = regCoreMinorDiameter
            grainLength -= exposedFaces * regDist
            
        if self.isCoreInverted():
            return minorFrustumDiameter, majorFrustumDiameter, grainLength

        return majorFrustumDiameter, minorFrustumDiameter, grainLength

    def getSurfaceAreaAtRegression(self, regDist):
        """Returns the surface area of the grain after it has regressed a linear distance of 'regDist'"""
        aftDiameter, forwardDiameter, length = self.getFrustumInfo(regDist)
        surfaceArea = geometry.frustumLateralSurfaceArea(aftDiameter, forwardDiameter, length)

        fullFaceArea = geometry.circleArea(self.props['diameter'].getValue())
        if self.props['inhibitedEnds'].getValue() in [InhibitedEnds.NEITHER, InhibitedEnds.BOTTOM]:
            surfaceArea += fullFaceArea - geometry.circleArea(forwardDiameter)
        if self.props['inhibitedEnds'].getValue() in [InhibitedEnds.NEITHER, InhibitedEnds.TOP]:
            surfaceArea += fullFaceArea - geometry.circleArea(aftDiameter)

        return surfaceArea

    def getVolumeAtRegression(self, regDist):
        """Returns the volume of propellant in the grain after it has regressed a linear distance 'regDist'"""
        aftDiameter, forwardDiameter, length = self.getFrustumInfo(regDist)
        frustumVolume = geometry.frustumVolume(aftDiameter, forwardDiameter, length)
        outerVolume = geometry.cylinderVolume(self.props['diameter'].getValue(), length)

        return outerVolume - frustumVolume

    def getWebLeft(self, regDist):
        """Returns the shortest distance the grain has to regress to burn out"""
        aftDiameter, forwardDiameter, length = self.getFrustumInfo(regDist)

        return (self.props['diameter'].getValue() - min(aftDiameter, forwardDiameter)) / 2

    def getMassFlow(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flow at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""

        # For now these grains are only allowed with inhibited faces, so we can ignore a lot of messy logic
        unsteppedFrustum = self.getFrustumInfo(regDist)
        steppedFrustum = self.getFrustumInfo(regDist + dRegDist)

        """These have to be reordered, because getFrustumInfo returns (aft, forward, length), but splitFrustum wants
        the position from the forward face"""
        unsteppedFrustum = (unsteppedFrustum[1], unsteppedFrustum[0], unsteppedFrustum[2])
        steppedFrustum = (steppedFrustum[1], steppedFrustum[0], steppedFrustum[2])

         # Note that this assumes the forward end of the grain is still at postition 0 - inhibited
        unsteppedPartialFrustum, _ = geometry.splitFrustum(*unsteppedFrustum, position)
        steppedPartialFrustum, _ = geometry.splitFrustum(*steppedFrustum, position)

        unsteppedVolume = geometry.frustumVolume(*unsteppedPartialFrustum)
        steppedVolume = geometry.frustumVolume(*steppedPartialFrustum)

        massFlow = (steppedVolume - unsteppedVolume) * density / dTime
        massFlow += massIn

        return massFlow, steppedPartialFrustum[1]

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flux at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""

        massFlow, portDiameter = self.getMassFlow(massIn, dTime, regDist, dRegDist, position, density)

        return massFlow / geometry.circleArea(portDiameter) # Index 1 is port diameter OR IS IT

    def getPeakMassFlux(self, massIn, dTime, regDist, dRegDist, density):
        """Uses the grain's mass flux method to return the max. Need to define this here because I'm not sure what
        it will look like"""

        forwardMassFlux = self.getMassFlux(massIn, dTime, regDist, dRegDist, self.getEndPositions(regDist)[0], density)
        aftMassFlux = self.getMassFlux(massIn, dTime, regDist, dRegDist, self.getEndPositions(regDist)[1], density)

        return max(forwardMassFlux, aftMassFlux)

    def getEndPositions(self, regDist):
        """Returns the positions of the grain ends relative to the original (unburned) grain top. Returns a tuple like
        (forward, aft)"""
        originalLength = self.props['length'].getValue()
        aftCoreDiameter, forwardCoreDiameter, currentLength = self.getFrustumInfo(regDist)
        inhibitedEnds = self.props['inhibitedEnds'].getValue()

        if self.isCoreInverted():
            if inhibitedEnds == InhibitedEnds.BOTTOM or inhibitedEnds == InhibitedEnds.BOTH:
                # Because all of the change in length is due to the forward end moving, the forward end's position is
                # just the amount the the grain has regressed by, The aft end stays where it started
                return (originalLength - currentLength, originalLength)

            # Neither or Top. In this case, the forward end moving accounts for almost all of the change in total grain
            # length, except for the aft face having moved up by `regDist`, so that quantity is subtracted from the
            # total change in grain length to get the forward end position
            return (originalLength - currentLength - regDist, originalLength - regDist)

        if inhibitedEnds == InhibitedEnds.TOP or inhibitedEnds == InhibitedEnds.BOTH:
            # All of the change in grain length is due to the aft face moving, so the forward face stays at 0 and the
            # aft face is at the regressed grain length
            return (0, currentLength)

        # Neither or Bottom
        return (regDist, regDist + currentLength)

    def getPortArea(self, regDist):
        """Returns the area of the grain's port when it has regressed a distance of 'regDist'"""
        aftCoreDiameter, _, _ = self.getFrustumInfo(regDist)

        return geometry.circleArea(aftCoreDiameter)

    def getDetailsString(self, lengthUnit=LengthUnit.METER):
        """Returns a short string describing the grain, formatted using the units that is passed in"""
        return 'Length: {}'.format(self.props['length'].dispFormat(lengthUnit))

    def simulationSetup(self, config):
        """Do anything needed to prepare this grain for simulation"""
        return None

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['aftCoreDiameter'].getValue() == self.props['forwardCoreDiameter'].getValue():
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameters cannot be the same, use a BATES for this case.'))
        if self.props['aftCoreDiameter'].getValue() > self.props['diameter'].getValue():
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Aft core diameter cannot be larger than grain diameter.'))
        if self.props['forwardCoreDiameter'].getValue() > self.props['diameter'].getValue():
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Forward core diameter cannot be larger than grain diameter.'))
        return errors
