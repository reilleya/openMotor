from . import grain, batesGrain, endBurningGrain
from .properties import *

import numpy as np
import skfmm
from skimage import measure
from matplotlib import pyplot as plt

def length(contour): # Adds up the length of each segment in a contour
    offset = np.roll(contour.T, 1, axis = 1)
    l = np.linalg.norm(contour.T - offset, axis = 0)
    return sum(list(l)[1:])

def clean(contour, m = 498): # Removes the points in a contour near the edge (inhibits the casting tube)
    offset = np.array([[500, 500]])
    l = np.linalg.norm(contour - offset, axis = 1)
    return contour[l < m]

class perforatedGrain(grain):
    geomName = 'PerfGrain'
    def __init__(self):
        super().__init__()
        self.props['inhibitedEnds'] = enumProperty('Inhibited ends', ['Neither', 'Top', 'Bottom', 'Both'])

        self.mapDim = 1001
        self.X, self.Y = np.meshgrid(np.linspace(-1, 1, self.mapDim), np.linspace(-1, 1, self.mapDim))
        self.mask = self.X**2 + self.Y**2 > 1
        self.coreMap = np.ones_like(self.X)
        self.regressionMap = None

    def getEndPositions(self, r):
        # Until there is some kind of enum prop, inhibited faces are handled like this:
        if self.props['inhibitedEnds'].getValue() == 'Neither': # Neither
            return [r, self.props['length'].getValue() - r]
        elif self.props['inhibitedEnds'].getValue() == 'Top': # Top
            return [0, self.props['length'].getValue() - r]
        elif self.props['inhibitedEnds'].getValue() == 'Bottom': # Bottom
            return [r, self.props['length'].getValue()]
        elif self.props['inhibitedEnds'].getValue() == 'Both':
            return [0, self.props['length'].getValue()]

    def normalize(self, value): # Used when transforming real unit quantities into self.X, self.Y coordinates
        return value / (0.5 * self.props['diameter'].getValue())

    def unNormalize(self, value):
        return (value / 2) * self.props['diameter'].getValue()

    def lengthToMap(self, value): # Used to convert meters to pixels
        return self.mapDim * (value / self.props['diameter'].getValue())

    def mapToLength(self, value): # Used to convert pixels to meters
        return self.props['diameter'].getValue() * (value / self.mapDim)

    def areaToMap(self, value): # Used to convert sqm to sq pixels
        return (self.mapDim ** 2) * (value / (self.props['diameter'].getValue() ** 2))

    def mapToArea(self, value): # Used to convert sq pixels to sqm
        return (self.props['diameter'].getValue() ** 2) * (value / (self.mapDim ** 2))

    def generateCoreMap(self):
        pass

    def generateRegressionMap(self):
        self.generateCoreMap()
        masked = np.ma.MaskedArray(self.coreMap, self.mask)
        plt.imshow(masked)
        plt.show()
        self.regressionMap = skfmm.distance(masked, dx=1e-3) * 2
        plt.imshow(self.regressionMap)
        plt.show()

    def getWebLeft(self, r):
        if self.regressionMap is None:
            self.generateRegressionMap()
        #print(np.amax(self.regressionMap))
        #print(self.unNormalize(np.amax(self.regressionMap)))
        #print(self.unNormalize(np.amax(self.regressionMap)) - r)
        #print('\n')

        wallLeft = self.unNormalize(np.amax(self.regressionMap)) - r

        lengthLeft = self.getRegressedLength(r)

        return min(lengthLeft, wallLeft)

    def getSurfaceAreaAtRegression(self, r):
        if self.regressionMap is None:
            self.generateRegressionMap()

        mapDist = self.normalize(r)

        valid = np.logical_not(self.mask)
        faceArea = self.mapToArea(np.count_nonzero(np.logical_and(self.regressionMap >= mapDist, valid)))

        corePerimeter = 0
        contours = measure.find_contours(self.regressionMap, mapDist, fully_connected='high')
        for contour in contours:
            contour = clean(contour)
            corePerimeter += self.mapToLength(length(contour))

        coreArea = corePerimeter * self.getRegressedLength(r)

        exposedFaces = 2
        if self.props['inhibitedEnds'].getValue() == 'Top' or self.props['inhibitedEnds'].getValue() == 'Bottom':
            exposedFaces = 1
        if self.props['inhibitedEnds'].getValue() == 'Both':
            exposedFaces = 0

        return coreArea + (exposedFaces * faceArea)
    
    def getVolumeAtRegression(self, r):
        if self.regressionMap is None:
            self.generateRegressionMap()
            
        mapDist = self.normalize(r)

        valid = np.logical_not(self.mask)
        faceArea = np.count_nonzero(np.logical_and(self.regressionMap >= mapDist, valid))

        return faceArea * self.getRegressedLength(r)

    def getMassFlux(self, massIn, dt, r, dr, position, density):
        return 0 # Todo: implement this!


class finocyl(perforatedGrain):
    geomName = 'Finocyl'
    def __init__(self):
        super().__init__()
        self.props['numFins'] = intProperty('Number of fins', '', 0, 64)
        self.props['finWidth'] = floatProperty('Fin width', 'm', 0, 1)
        self.props['finLength'] = floatProperty('Fin length', 'm', 0, 1)
        self.props['coreDiameter'] = floatProperty('Core diameter', 'm', 0, 1)

    def generateCoreMap(self):
        coreRadius = self.normalize(self.props['coreDiameter'].getValue()) / 2
        numFins = self.props['numFins'].getValue()
        finWidth = self.normalize(self.props['finWidth'].getValue())
        finLength = self.normalize(self.props['finLength'].getValue()) + coreRadius # The user enters the length that the fin protrudes from the core, so we add the radius on

        # Open up core
        self.coreMap[self.X**2 + self.Y**2 < coreRadius**2] = 0

        # Add fins
        for i in range(0, numFins):
            th = 2 * np.pi / numFins * i
            # Initialize a vector pointing along the fin
            a = np.cos(th)
            b = np.sin(th)
            # Select all points within half the width of the vector
            vect = abs(a*self.X + b*self.Y) < finWidth / 2
            # Set up two perpendicular vectors to cap off the ends
            near = (b * self.X) - (a * self.Y) > 0 # Inside of the core
            far = (b * self.X) - (a * self.Y) < finLength # At the casting tube end of the vector
            ends = np.logical_and(far, near)
            # Open up the fin
            self.coreMap[np.logical_and(vect, ends)] = 0

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Core: ' + self.props['coreDiameter'].dispFormat(lengthUnit) + ', Fins: ' + str(self.props['numFins'].getValue())

# TODO: Move this to a better place when grain.py/perforatedGrain.py get reorganized
# Generate grain geometry name -> constructor lookup table
grainTypes = {}
grainClasses = [batesGrain, endBurningGrain, finocyl]
for grainType in grainClasses:
    grainTypes[grainType.geomName] = grainType

