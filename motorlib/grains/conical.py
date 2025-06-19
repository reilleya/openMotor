"""BATES submodule"""

from math import atan, cos, tan

from ..grain import Grain
from .. import geometry
from ..simResult import SimAlert, SimAlertLevel, SimAlertType
from ..properties import FloatProperty, EnumProperty

class ConicalGrain(Grain):
    """A conical grain is similar to a BATES grain except it has different core diameters at each end."""
    geomName = "Conical"
    def __init__(self):
        super().__init__()
        self.props['forwardCoreDiameter'] = FloatProperty('Forward Core Diameter', 'm', 0, 1)
        self.props['aftCoreDiameter'] = FloatProperty('Aft Core Diameter', 'm', 0, 1)
        self.props['inhibitedEnds'] = EnumProperty('Inhibited ends', ['Neither', 'Top', 'Bottom', 'Both'])

    def isCoreInverted(self):
        """A simple helper that returns 'true' if the core's foward diameter is larger than its aft diameter"""
        return self.props['forwardCoreDiameter'].getValue() > self.props['aftCoreDiameter'].getValue()

    def getFrustumInfo(self, regDist):
        """Returns the dimensions of the grain's core at a given regression depth. The core is always a frustum and is
        returned as the forward diameter, aft diameter, and length"""
        grainDiameter = self.props['diameter'].getValue()
        aftDiameter = self.props['aftCoreDiameter'].getValue()
        forwardDiameter = self.props['forwardCoreDiameter'].getValue()
        grainLength = self.props['length'].getValue()

        inhibitedEnds = self.props['inhibitedEnds'].getValue()
        forward_exposed = (inhibitedEnds in ('Neither', 'Bottom'))
        aft_exposed     = (inhibitedEnds in ('Neither', 'Top'))

        # These calculations are easiest if we work in terms of the core's "large end" and "small end"
        if self.isCoreInverted():
            coreMajorDiameter, coreMinorDiameter = forwardDiameter, aftDiameter
            major_exposed, minor_exposed = forward_exposed, aft_exposed
        else:
            coreMajorDiameter, coreMinorDiameter = aftDiameter, forwardDiameter
            major_exposed, minor_exposed = aft_exposed, forward_exposed

        # Calculate the half angle of the core. This is done with without accounting for regression because it doesn't
        # change with regression
        angle = atan((coreMajorDiameter - coreMinorDiameter) / (2 * grainLength))

        # Expand both core diameters by the radial component of the core's regression vector. This is allowed to expand
        # beyond the casting tube as that condition is checked in a later step
        regCoreMajorDiameter = coreMajorDiameter + (regDist * 2 * cos(angle)) - major_exposed * (regDist * 2 * tan(angle))
        regCoreMinorDiameter = coreMinorDiameter + (regDist * 2 * cos(angle)) + minor_exposed * (regDist * 2 * tan(angle))
 
        # This is case where the larger core diameter has grown beyond the casting tube diameter. Once this happens,
        # the diameter of the large end of the core is clamped at the grain diameter and the length is changed to keep
        # the angle constant, which accounts for the regression of the grain at the major end.
        if regCoreMajorDiameter >= grainDiameter:
            majorFrustumDiameter = grainDiameter

        # If the large end of the core hasn't reached the casting tube, we know that the small end hasn't either. In
        # this case we just return the current core diameters, and a length calculated from the inhibitor configuration
        else:
            majorFrustumDiameter = regCoreMajorDiameter

        # Minor frustum diameter is never clamped (the point when it would clamp is burnout), so we can use it to determine
        # the length of the grain at any regression depth
        minorFrustumDiameter = regCoreMinorDiameter
        grainLength = (majorFrustumDiameter - minorFrustumDiameter) / (2 * tan(angle))
        
        if self.isCoreInverted():
            return majorFrustumDiameter, minorFrustumDiameter, grainLength

        return minorFrustumDiameter, majorFrustumDiameter, grainLength

    def getSurfaceAreaAtRegression(self, regDist):
        """Returns the surface area of the grain after it has regressed a linear distance of 'regDist'"""
        forwardDiameter, aftDiameter, length = self.getFrustumInfo(regDist)
        surfaceArea = geometry.frustumLateralSurfaceArea(forwardDiameter, aftDiameter, length)

        fullFaceArea = geometry.circleArea(self.props['diameter'].getValue())
        if self.props['inhibitedEnds'].getValue() in ('Neither', 'Bottom'):
            surfaceArea += fullFaceArea - geometry.circleArea(forwardDiameter)
        if self.props['inhibitedEnds'].getValue() in ('Neither', 'Top'):
            surfaceArea += fullFaceArea - geometry.circleArea(aftDiameter)

        return surfaceArea

    def getVolumeAtRegression(self, regDist):
        """Returns the volume of propellant in the grain after it has regressed a linear distance 'regDist'"""
        forwardDiameter, aftDiameter, length = self.getFrustumInfo(regDist)
        frustumVolume = geometry.frustumVolume(forwardDiameter, aftDiameter, length)
        outerVolume = geometry.cylinderVolume(self.props['diameter'].getValue(), length)

        return outerVolume - frustumVolume

    def getWebLeft(self, regDist):
        """Returns the shortest distance the grain has to regress to burn out"""
        forwardDiameter, aftDiameter, length = self.getFrustumInfo(regDist)
        wallLeft = (self.props['diameter'].getValue() - min(aftDiameter, forwardDiameter)) / 2

        if self.props['inhibitedEnds'].getValue() == 'Both':
            return wallLeft

        return min(wallLeft, length)

    def getMassFlow(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flow at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""
        unsteppedFrustum = self.getFrustumInfo(regDist)
        steppedFrustum = self.getFrustumInfo(regDist + dRegDist)
        grainDiameter = self.props['diameter'].getValue()
        aftUninhibited = (self.props['inhibitedEnds'].getValue() in ('Neither', 'Top'))
        foreUninhibited = (self.props['inhibitedEnds'].getValue() in ('Neither', 'Bottom'))

        if position > dRegDist:
            unsteppedPartialFrustum, _ = geometry.splitFrustum(*unsteppedFrustum, position - dRegDist * aftUninhibited)
            steppedPartialFrustum, _ = geometry.splitFrustum(*steppedFrustum, steppedFrustum[2])
        else:
            unsteppedPartialFrustum, _ = geometry.splitFrustum(*unsteppedFrustum, position + dRegDist * foreUninhibited)
            steppedPartialFrustum, _ = geometry.splitFrustum(*steppedFrustum, position)
        
        unsteppedFrustumVolume = geometry.frustumVolume(*unsteppedPartialFrustum)
        steppedFrustumVolume = geometry.frustumVolume(*steppedPartialFrustum)

        unsteppedPropVolume = geometry.cylinderVolume(grainDiameter, unsteppedPartialFrustum[2]) - unsteppedFrustumVolume
        steppedPropVolume = geometry.cylinderVolume(grainDiameter, steppedPartialFrustum[2]) - steppedFrustumVolume

        massFlow = (unsteppedPropVolume - steppedPropVolume) * density / dTime
        massFlow += massIn

        return massFlow, steppedPartialFrustum[1]

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flux at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""
        massFlow, portDiameter = self.getMassFlow(massIn, dTime, regDist, dRegDist, position, density)

        return massFlow / geometry.circleArea(portDiameter)

    def getPeakMassFlux(self, massIn, dTime, regDist, dRegDist, density):
        """Uses the grain's mass flux method to return the max. Need to define this here because I'm not sure what
        it will look like"""
        _, _, length = self.getFrustumInfo(regDist)
        
        forwardMassFlux = self.getMassFlux(massIn, dTime, regDist, dRegDist, 0, density)
        aftMassFlux = self.getMassFlux(massIn, dTime, regDist, dRegDist, length, density)

        return max(forwardMassFlux, aftMassFlux)

    def getEndPositions(self, regDist):
        """Returns the positions of the grain ends relative to the original (unburned) grain top. Returns a tuple like
        (forward, aft)"""
        originalLength = self.props['length'].getValue()
        grainDiameter = self.props['diameter'].getValue()
        forwardCoreDiameter, aftCoreDiameter, currentLength = self.getFrustumInfo(regDist)

        inhibitedEnds = self.props['inhibitedEnds'].getValue()
        forward_exposed = (inhibitedEnds in ('Neither', 'Bottom'))
        aft_exposed     = (inhibitedEnds in ('Neither', 'Top'))

        # These calculations are easiest if we work in terms of the core's "large end" and "small end"
        if self.isCoreInverted():
            coreMajorDiameter, coreMinorDiameter = forwardCoreDiameter, aftCoreDiameter
            major_exposed, minor_exposed = forward_exposed, aft_exposed
        else:
            coreMajorDiameter, coreMinorDiameter = aftCoreDiameter, forwardCoreDiameter
            major_exposed, minor_exposed = aft_exposed, forward_exposed

        # Un-clamped major diameter        
        if coreMajorDiameter < grainDiameter:
            forward_regression, aft_regression = forward_exposed * regDist, aft_exposed * regDist
            return forward_regression, originalLength - aft_regression
        else:
            minor_regression = minor_exposed * regDist
            major_regression = (originalLength - currentLength) - minor_regression
            forward_regression, aft_regression = (major_regression, minor_regression) if self.isCoreInverted() else (minor_regression, major_regression)
            return forward_regression, originalLength - aft_regression

    def getPortArea(self, regDist):
        """Returns the area of the grain's port when it has regressed a distance of 'regDist'"""
        _, aftCoreDiameter, _ = self.getFrustumInfo(regDist)

        return geometry.circleArea(aftCoreDiameter)

    def getDetailsString(self, lengthUnit='m'):
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
