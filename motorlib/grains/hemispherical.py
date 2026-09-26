"""Axisymmetric hemispherical grains used to close capsule-shaped motors."""

import math

import numpy as np
import skfmm
from skimage import measure

from .. import geometry
from ..constants import maximumRefDiameter
from ..grain import Grain
from ..properties import FloatProperty
from ..simResult import SimAlert, SimAlertLevel, SimAlertType


class AxisymmetricHemisphericalGrain(Grain):
    """Shared analytical model for hemispherical end grains.

    Area and volume are evaluated exactly. The distance field is retained only
    to draw the two-dimensional axial half-section and regression contours.
    """

    geomName = None
    hasOutlet = False

    def __init__(self):
        super().__init__()
        self.props["portDiameter"] = FloatProperty(
            "Mating port diameter", "m", 0, maximumRefDiameter
        )
        self.mapDim = None
        self.radial = None
        self.axial = None
        self.mask = None
        self.coreMap = None
        self.regressionMap = None
        self.wallWeb = 0
        self.geometryInitialized = False
        self._syncLength()

    def _syncLength(self):
        length = self.props["diameter"].getValue() / 2
        self.props["length"].min = length
        self.props["length"].max = length
        self.props["length"].value = length

    def setProperty(self, prop, value):
        if prop == "length":
            return
        super().setProperty(prop, value)
        self.geometryInitialized = False
        if prop == "diameter":
            self._syncLength()

    def setProperties(self, props):
        for prop, value in props.items():
            if prop != "length":
                self.setProperty(prop, value)
        self._syncLength()

    def _getVoidMask(self, radial, axial):
        portRadius = self.props["portDiameter"].getValue() / 2
        return radial**2 + axial**2 <= portRadius**2

    def _getWallWeb(self):
        radius = self.props["diameter"].getValue() / 2
        portRadius = self.props["portDiameter"].getValue() / 2
        return max(radius - portRadius, 0)

    def _buildGeometry(self, mapDim):
        radius = self.props["diameter"].getValue() / 2
        self.mapDim = mapDim

        radialStep = radius / mapDim
        axialStep = radius / mapDim
        radialValues = (np.arange(mapDim) + 0.5) * radialStep
        axialValues = (np.arange(mapDim) + 0.5) * axialStep
        self.radial, self.axial = np.meshgrid(radialValues, axialValues)

        outer = self.radial**2 + self.axial**2 <= radius**2
        void = self._getVoidMask(self.radial, self.axial)
        self.mask = np.logical_not(outer)
        self.coreMap = np.where(void, -1.0, 1.0)

        levelSet = np.ma.MaskedArray(self.coreMap, self.mask)
        self.regressionMap = skfmm.distance(
            levelSet, dx=(axialStep, radialStep)
        )
        self.wallWeb = self._getWallWeb()
        self.geometryInitialized = True

    def simulationSetup(self, config):
        self.mapDim = config.getProperty("mapDim")
        self.wallWeb = self._getWallWeb()
        self.geometryInitialized = True

    def _ensureGeometry(self):
        if not self.geometryInitialized:
            raise ValueError("Grain geometry must be initialized before use")

    def getSurfaceAreaAtRegression(self, regDist):
        self._ensureGeometry()
        if regDist >= self.wallWeb:
            return 0
        portRadius = self.props["portDiameter"].getValue() / 2
        regressedRadius = portRadius + max(regDist, 0)
        return 2 * math.pi * regressedRadius**2

    def getVolumeAtRegression(self, regDist):
        self._ensureGeometry()
        if regDist >= self.wallWeb:
            return 0
        radius = self.props["diameter"].getValue() / 2
        portRadius = self.props["portDiameter"].getValue() / 2
        regressedRadius = portRadius + max(regDist, 0)
        return (2 / 3) * math.pi * (
            radius**3 - regressedRadius**3
        )

    def getWebLeft(self, regDist):
        self._ensureGeometry()
        return max(self.wallWeb - regDist, 0)

    def getEndPositions(self, regDist):
        return (0, self.props["length"].getValue())

    def getMatingPortArea(self, regDist):
        diameter = min(
            self.props["portDiameter"].getValue() + 2 * regDist,
            self.props["diameter"].getValue(),
        )
        return geometry.circleArea(diameter)

    def getPortArea(self, regDist):
        return self.getMatingPortArea(regDist)

    def getMassFlux(
        self, massIn, dTime, regDist, dRegDist, position, density
    ):
        massFlow = massIn + (
            self.getVolumeSlice(regDist, dRegDist) * density / dTime
        )
        portArea = self.getPortArea(regDist + dRegDist)
        return massFlow / portArea if portArea > 0 else 0

    def getPeakMassFlux(self, massIn, dTime, regDist, dRegDist, density):
        return self.getMassFlux(
            massIn,
            dTime,
            regDist,
            dRegDist,
            self.props["length"].getValue(),
            density,
        )

    def getGrainBoundingVolume(self):
        radius = self.props["diameter"].getValue() / 2
        return (2 / 3) * math.pi * radius**3

    def getDetailsString(self, lengthUnit="m"):
        return "Hemisphere: {}, Port: {}".format(
            self.props["diameter"].dispFormat(lengthUnit),
            self.props["portDiameter"].dispFormat(lengthUnit),
        )

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        diameter = self.props["diameter"].getValue()
        portDiameter = self.props["portDiameter"].getValue()
        if portDiameter == 0:
            errors.append(
                SimAlert(
                    SimAlertLevel.ERROR,
                    SimAlertType.GEOMETRY,
                    "Mating port diameter must not be 0",
                )
            )
        if portDiameter >= diameter and diameter > 0:
            errors.append(
                SimAlert(
                    SimAlertLevel.ERROR,
                    SimAlertType.GEOMETRY,
                    "Mating port diameter must be less than grain diameter",
                )
            )
        return errors

    def getFaceImage(self, mapDim):
        self._buildGeometry(mapDim)
        return self._mirrorMap(np.ma.MaskedArray(self.coreMap, self.mask))

    def _mirrorMap(self, data):
        return np.ma.concatenate((np.fliplr(data), data), axis=1)

    def getRegressionData(self, mapDim, numContours=15, coreBlack=True):
        self._buildGeometry(mapDim)
        core = np.ma.MaskedArray(self.coreMap, self.mask)
        regression = np.ma.MaskedArray(self.regressionMap, self.mask)
        mirroredCore = self._mirrorMap(core)
        mirroredRegression = self._mirrorMap(regression)

        contours = []
        contourAreas = {}
        if self.wallWeb > 0:
            for level in np.linspace(0, self.wallWeb, numContours):
                image = mirroredRegression.filled(self.wallWeb + 1)
                contours.append(measure.find_contours(image, level))
                contourAreas[level] = self.getSurfaceAreaAtRegression(level)

        if coreBlack:
            mirroredRegression = mirroredRegression.copy()
            mirroredRegression[np.where(mirroredCore < 0)] = self.wallWeb

        return mirroredCore, mirroredRegression, contours, contourAreas


class TopHemisphericalGrain(AxisymmetricHemisphericalGrain):
    """Forward capsule cap with a closed hemispherical combustion cavity."""

    geomName = "Top Hemispherical Grain"


class BottomHemisphericalGrain(AxisymmetricHemisphericalGrain):
    """Aft capsule cap with a hemispherical cavity and axial outlet."""

    geomName = "Bottom Hemispherical Grain"
    hasOutlet = True

    def __init__(self):
        super().__init__()
        self.props["outletDiameter"] = FloatProperty(
            "Outlet diameter", "m", 0, maximumRefDiameter
        )

    def _getVoidMask(self, radial, axial):
        hemisphere = super()._getVoidMask(radial, axial)
        outletRadius = self.props["outletDiameter"].getValue() / 2
        outlet = radial <= outletRadius
        return np.logical_or(hemisphere, outlet)

    def _getWallWeb(self):
        radius = self.props["diameter"].getValue() / 2
        portRadius = self.props["portDiameter"].getValue() / 2
        outletRadius = self.props["outletDiameter"].getValue() / 2
        return max(radius - max(portRadius, outletRadius), 0)

    def getSurfaceAreaAtRegression(self, regDist):
        self._ensureGeometry()
        if regDist >= self.wallWeb:
            return 0

        radius = self.props["diameter"].getValue() / 2
        portRadius = self.props["portDiameter"].getValue() / 2
        outletRadius = self.props["outletDiameter"].getValue() / 2
        regDist = max(regDist, 0)
        sphereRadius = portRadius + regDist
        cylinderRadius = outletRadius + regDist

        outerHeight = math.sqrt(max(radius**2 - cylinderRadius**2, 0))
        intersectionHeight = math.sqrt(
            max(sphereRadius**2 - cylinderRadius**2, 0)
        )
        sphereArea = 2 * math.pi * sphereRadius * intersectionHeight
        cylinderArea = (
            2
            * math.pi
            * cylinderRadius
            * (outerHeight - intersectionHeight)
        )
        return max(sphereArea + cylinderArea, 0)

    def getVolumeAtRegression(self, regDist):
        self._ensureGeometry()
        if regDist >= self.wallWeb:
            return 0

        radius = self.props["diameter"].getValue() / 2
        portRadius = self.props["portDiameter"].getValue() / 2
        outletRadius = self.props["outletDiameter"].getValue() / 2
        regDist = max(regDist, 0)
        sphereRadius = portRadius + regDist
        cylinderRadius = outletRadius + regDist

        outerVolumeTerm = max(radius**2 - cylinderRadius**2, 0) ** 1.5
        innerVolumeTerm = max(
            sphereRadius**2 - cylinderRadius**2, 0
        ) ** 1.5
        return (2 / 3) * math.pi * max(
            outerVolumeTerm - innerVolumeTerm, 0
        )

    def getPortArea(self, regDist):
        diameter = min(
            self.props["outletDiameter"].getValue() + 2 * regDist,
            self.props["diameter"].getValue(),
        )
        return geometry.circleArea(diameter)

    def getDetailsString(self, lengthUnit="m"):
        return "{}, Outlet: {}".format(
            super().getDetailsString(lengthUnit),
            self.props["outletDiameter"].dispFormat(lengthUnit),
        )

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        outletDiameter = self.props["outletDiameter"].getValue()
        diameter = self.props["diameter"].getValue()
        if outletDiameter == 0:
            errors.append(
                SimAlert(
                    SimAlertLevel.ERROR,
                    SimAlertType.GEOMETRY,
                    "Outlet diameter must not be 0",
                )
            )
        if outletDiameter >= diameter and diameter > 0:
            errors.append(
                SimAlert(
                    SimAlertLevel.ERROR,
                    SimAlertType.GEOMETRY,
                    "Outlet diameter must be less than grain diameter",
                )
            )
        return errors
