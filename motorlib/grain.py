"""This module includes the base classes from which all grain classes should inherit. None of these objects
should be instantiated directly."""

from abc import abstractmethod

import numpy as np
import skfmm
from skimage import measure
from scipy.signal import savgol_filter
from scipy import interpolate

from . import geometry
from .simResult import SimAlert, SimAlertLevel, SimAlertType
from .properties import FloatProperty, EnumProperty, PropertyCollection

class Grain(PropertyCollection):
    """A basic propellant grain. This is the class that all grains inherit from. It provides a few properties and
    composed methods but otherwise it is up to the subclass to make a functional grain."""
    geomName = None
    def __init__(self):
        super().__init__()
        self.props['diameter'] = FloatProperty('Diameter', 'm', 0, 1)
        self.props['length'] = FloatProperty('Length', 'm', 0, 3)

    def getVolumeSlice(self, regDist, dRegDist):
        """Returns the amount of propellant volume consumed as the grain regresses from a distance of 'regDist' to
        regDist + dRegDist"""
        return self.getVolumeAtRegression(regDist) - self.getVolumeAtRegression(regDist + dRegDist)

    @abstractmethod
    def getSurfaceAreaAtRegression(self, regDist):
        """Returns the surface area of the grain after it has regressed a linear distance of 'regDist'"""

    @abstractmethod
    def getVolumeAtRegression(self, regDist):
        """Returns the volume of propellant in the grain after it has regressed a linear distance 'regDist'"""

    @abstractmethod
    def getWebLeft(self, regDist):
        """Returns the shortest distance the grain has to regress to burn out"""

    def isWebLeft(self, regDist, burnoutThres=0.00001):
        """Returns True if the grain has propellant left to burn after it has regressed a distance of 'regDist'"""
        return self.getWebLeft(regDist) > burnoutThres

    @abstractmethod
    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        """Returns the mass flux at a point along the grain. Takes in the mass flow into the grain, a timestep, the
        distance the grain has regressed so far, the additional distance it will regress during the timestep, a
        position along the grain measured from the head end, and the density of the propellant."""

    def getPeakMassFlux(self, massIn, dTime, regDist, dRegDist, density):
        """Uses the grain's mass flux method to return the max. Assumes that it will be at the port of the grain!"""
        return self.getMassFlux(massIn, dTime, regDist, dRegDist, self.getEndPositions(regDist)[1], density)

    @abstractmethod
    def getEndPositions(self, regDist):
        """Returns the positions of the grain ends relative to the original (unburned) grain top"""

    @abstractmethod
    def getPortArea(self, regDist):
        """Returns the area of the grain's port when it has regressed a distance of 'regDist'"""

    def getRegressedLength(self, regDist):
        """Returns the length of the grain when it has regressed a distance of 'regDist', taking any possible
        inhibition into account."""
        endPos = self.getEndPositions(regDist)
        return endPos[1] - endPos[0]

    def getDetailsString(self, lengthUnit='m'):
        """Returns a short string describing the grain, formatted using the units that is passed in"""
        return 'Length: {}'.format(self.props['length'].dispFormat(lengthUnit))

    @abstractmethod
    def simulationSetup(self, config):
        """Do anything needed to prepare this grain for simulation"""

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

    def getGrainBoundingVolume(self):
        """Returns the volume of the bounding cylinder around the grain"""
        return geometry.cylinderVolume(self.props['diameter'].getValue(), self.props['length'].getValue())

    def getFreeVolume(self, regDist):
        """Returns the amount of empty (non-propellant) volume in bounding cylinder of the grain for a given regression
        depth."""
        return float(self.getGrainBoundingVolume() - self.getVolumeAtRegression(regDist))


class PerforatedGrain(Grain):
    """A grain with a hole of some shape through the center. Adds abstract methods related to the core to the
    basic grain class """
    geomName = 'perfGrain'
    def __init__(self):
        super().__init__()
        self.props['inhibitedEnds'] = EnumProperty('Inhibited ends', ['Neither', 'Top', 'Bottom', 'Both'])
        self.wallWeb = 0 # Max distance from the core to the wall

    def getEndPositions(self, regDist):
        if self.props['inhibitedEnds'].getValue() == 'Neither': # Neither
            return (regDist, self.props['length'].getValue() - regDist)
        if self.props['inhibitedEnds'].getValue() == 'Top': # Top
            return (0, self.props['length'].getValue() - regDist)
        if self.props['inhibitedEnds'].getValue() == 'Bottom': # Bottom
            return (regDist, self.props['length'].getValue())
        if self.props['inhibitedEnds'].getValue() == 'Both':
            return (0, self.props['length'].getValue())
        # The enum should prevent this from even being raised, but to cover the case where it somehow gets set wrong
        raise ValueError('Invalid number of faces inhibited')

    @abstractmethod
    def getCorePerimeter(self, regDist):
        """Returns the perimeter of the core after the grain has regressed a distance of 'regDist'."""

    @abstractmethod
    def getFaceArea(self, regDist):
        """Returns the area of the grain face after it has regressed a distance of 'regDist'. This is the
        same as the area of an equal-diameter endburning grain minus the grain's port area."""

    def getCoreSurfaceArea(self, regDist):
        """Returns the surface area of the grain's core after it has regressed a distance of 'regDist'"""
        corePerimeter = self.getCorePerimeter(regDist)
        coreArea = corePerimeter * self.getRegressedLength(regDist)
        return coreArea

    def getWebLeft(self, regDist):
        wallLeft = self.wallWeb - regDist
        if self.props['inhibitedEnds'].getValue() == 'Both':
            return wallLeft
        lengthLeft = self.getRegressedLength(regDist)
        return min(lengthLeft, wallLeft)

    def getSurfaceAreaAtRegression(self, regDist):
        faceArea = self.getFaceArea(regDist)
        coreArea = self.getCoreSurfaceArea(regDist)

        exposedFaces = 2
        if self.props['inhibitedEnds'].getValue() == 'Top' or self.props['inhibitedEnds'].getValue() == 'Bottom':
            exposedFaces = 1
        if self.props['inhibitedEnds'].getValue() == 'Both':
            exposedFaces = 0

        return coreArea + (exposedFaces * faceArea)

    def getVolumeAtRegression(self, regDist):
        faceArea = self.getFaceArea(regDist)
        return faceArea * self.getRegressedLength(regDist)

    def getPortArea(self, regDist):
        faceArea = self.getFaceArea(regDist)
        uncored = geometry.circleArea(self.props['diameter'].getValue())
        return uncored - faceArea

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        diameter = self.props['diameter'].getValue()

        endPos = self.getEndPositions(regDist)
        # If a position above the top face is queried, the mass flow is just the input mass and the
        # diameter is the casting tube
        if position < endPos[0]:
            return massIn / geometry.circleArea(diameter)
        # If a position in the grain is queried, the mass flow is the input mass, from the top face,
        # and from the tube up to the point. The diameter is the core.
        if position <= endPos[1]:
            if self.props['inhibitedEnds'].getValue() == 'Top': # Top inhibited
                top = 0
                countedCoreLength = position
            else:
                top = self.getFaceArea(regDist + dRegDist) * dRegDist * density
                countedCoreLength = position - (endPos[0] + dRegDist)
            # This block gets the mass of propellant the core burns in the step.
            core = ((self.getPortArea(regDist + dRegDist) * countedCoreLength)
                - (self.getPortArea(regDist) * countedCoreLength))
            core *= density

            massFlow = massIn + ((top + core) / dTime)
            return massFlow / self.getPortArea(regDist + dRegDist)
        # A position past the grain end was specified, so the mass flow includes the input mass flow
        # and all mass produced by the grain. Diameter is the casting tube.
        massFlow = massIn + (self.getVolumeSlice(regDist, dRegDist) * density / dTime)
        return massFlow / geometry.circleArea(diameter)

    @abstractmethod
    def getFaceImage(self, mapDim):
        """Returns an image of the grain's cross section, with resolution (mapDim, mapDim)."""

    @abstractmethod
    def getRegressionData(self, mapDim, numContours=15, coreBlack=True):
        """Returns a tuple that includes a grain face image as described in 'getFaceImage', a regression map
        where color maps to regression depth, a list of contours (lists of (x,y) points in image space) of
        equal regression depth, and a list of corresponding contour lengths. The contours are equally spaced
        between 0 regression and burnout."""


class FmmGrain(PerforatedGrain):
    """A grain that uses the fast marching method to calculate its regression. All a subclass has to do is
    provide an implementation of generateCoreMap that makes an image of a cross section of the grain."""
    geomName = 'fmmGrain'
    def __init__(self):
        super().__init__()
        self.mapDim = 1001
        self.mapX, self.mapY = None, None
        self.mask = None
        self.coreMap = None
        self.regressionMap = None
        self.faceArea = None

    def normalize(self, value):
        """Transforms real unit quantities into self.mapX, self.mapY coordinates. For use in indexing into the
        coremap."""
        return value / (0.5 * self.props['diameter'].getValue())

    def unNormalize(self, value):
        """Transforms self.mapX, self.mapY coordinates to real unit quantities. Used to determine real lengths in
        coremap."""
        return (value / 2) * self.props['diameter'].getValue()

    def lengthToMap(self, value):
        """Converts meters to pixels. Used to compare real distances to pixel distances in the regression map."""
        return self.mapDim * (value / self.props['diameter'].getValue())

    def mapToLength(self, value):
        """Converts pixels to meters. Used to extract real distances from pixel distances such as contour lengths"""
        return self.props['diameter'].getValue() * (value / self.mapDim)

    def areaToMap(self, value):
        """Used to convert sqm to sq pixels, like on the regression map."""
        return (self.mapDim ** 2) * (value / (self.props['diameter'].getValue() ** 2))

    def mapToArea(self, value):
        """Used to convert sq pixels to sqm. For extracting real areas from the regression map."""
        return (self.props['diameter'].getValue() ** 2) * (value / (self.mapDim ** 2))

    def initGeometry(self, mapDim):
        """Set up an empty core map and reset the regression map. Takes in the dimension of both maps."""
        if mapDim < 64:
            raise ValueError('Map dimension must be 64 or larger to get good results')
        self.mapDim = mapDim
        self.mapX, self.mapY = np.meshgrid(np.linspace(-1, 1, self.mapDim), np.linspace(-1, 1, self.mapDim))
        self.mask = self.mapX**2 + self.mapY**2 > 1
        self.coreMap = np.ones_like(self.mapX)
        self.regressionMap = None

    @abstractmethod
    def generateCoreMap(self):
        """Use self.mapX and self.mapY to generate an image of the grain cross section in self.coreMap. A 0 in the image
        means propellant, and a 1 means no propellant."""

    def simulationSetup(self, config):
        mapSize = config.getProperty("mapDim")

        self.initGeometry(mapSize)
        self.generateCoreMap()
        self.generateRegressionMap()

    def generateRegressionMap(self):
        """Uses the fast marching method to generate an image of how the grain regresses from the core map. The map
        is stored under self.regressionMap."""
        masked = np.ma.MaskedArray(self.coreMap, self.mask)
        cellSize = 1 / self.mapDim
        self.regressionMap = skfmm.distance(masked, dx=cellSize) * 2
        maxDist = np.amax(self.regressionMap)
        self.wallWeb = self.unNormalize(maxDist)
        faceArea = []
        polled = []
        valid = np.logical_not(self.mask)
        for i in range(int(maxDist * self.mapDim) + 2):
            polled.append(i / self.mapDim)
            faceArea.append(self.mapToArea(np.count_nonzero(np.logical_and(self.regressionMap > (i / self.mapDim), valid))))
        self.faceArea = savgol_filter(faceArea, 31, 5)
        self.faceAreaFunc = interpolate.interp1d(polled, self.faceArea)

    def getCorePerimeter(self, regDist):
        mapDist = self.normalize(regDist)

        corePerimeter = 0
        contours = measure.find_contours(self.regressionMap, mapDist, fully_connected='low')
        for contour in contours:
            corePerimeter += self.mapToLength(geometry.length(contour, self.mapDim))

        return corePerimeter

    def getFaceArea(self, regDist):
        mapDist = self.normalize(regDist)
        index = int(mapDist * self.mapDim)
        if index >= len(self.faceArea) - 1:
            return 0 # Past burnout
        return self.faceAreaFunc(mapDist)

    def getFaceImage(self, mapDim):
        self.initGeometry(mapDim)
        self.generateCoreMap()
        masked = np.ma.MaskedArray(self.coreMap, self.mask)
        return masked

    def getRegressionData(self, mapDim, numContours=15, coreBlack=True):
        self.initGeometry(mapDim)
        self.generateCoreMap()

        masked = np.ma.MaskedArray(self.coreMap, self.mask)
        regressionMap = None
        contours = []
        contourLengths = {}

        try:
            self.generateRegressionMap()

            regmax = np.amax(self.regressionMap)

            regressionMap = self.regressionMap[:, :].copy()
            if coreBlack:
                regressionMap[np.where(self.coreMap == 0)] = regmax # Make the core black
            regressionMap = np.ma.MaskedArray(regressionMap, self.mask)

            for dist in np.linspace(0, regmax, numContours):
                contours.append([])
                contourLengths[dist] = 0
                layerContours = measure.find_contours(self.regressionMap, dist, fully_connected='low')
                for contour in layerContours:
                    contours[-1].append(geometry.clean(contour, self.mapDim, 3))
                    contourLengths[dist] += geometry.length(contour, self.mapDim)

        except ValueError as exc: # If there aren't any contours, do nothing
            print(exc)

        return (masked, regressionMap, contours, contourLengths)
