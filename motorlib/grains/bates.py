from .. import perforatedGrain
from .. import geometry
from .. import simAlert, simAlertLevel, simAlertType
from ..properties import *

import numpy as np
import skfmm
from skimage import measure

class batesGrain(perforatedGrain):
    geomName = "BATES"
    def __init__(self):
        super().__init__()
        self.props['coreDiameter'] = floatProperty('Core Diameter', 'm', 0, 1)

    def simulationSetup(self, preferences):
        self.wallWeb = (self.props['diameter'].getValue() - self.props['coreDiameter'].getValue()) / 2

    def getCorePerimeter(self, r):
        return geometry.circlePerimeter(self.props['coreDiameter'].getValue() + (2 * r))

    def getFaceArea(self, r):
        return geometry.circleArea(self.props['diameter'].getValue()) - geometry.circleArea(self.props['coreDiameter'].getValue() + (2 * r))

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit) + ', Core: ' + self.props['coreDiameter'].dispFormat(lengthUnit)

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['coreDiameter'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self.props['coreDiameter'].getValue() >= self.props['diameter'].getValue():
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Core diameter must be less than grain diameter'))
        return errors

    # These two functions have a lot of code reuse, but it is worth it because making BATES an fmmGrain would make it way slower
    def getFaceImage(self, mapDim):
        X, Y = np.meshgrid(np.linspace(-1, 1, mapDim), np.linspace(-1, 1, mapDim))
        mask = X**2 + Y**2 > 1
        coreMap = np.ones_like(X)

        # Normalize core diameter
        coreRadius = (self.props['coreDiameter'].getValue() / (0.5 * self.props['diameter'].getValue())) / 2

        # Open up core
        coreMap[X**2 + Y**2 < coreRadius**2] = 0
        maskedMap = np.ma.MaskedArray(coreMap, mask)

        return maskedMap

    def getRegressionData(self, mapDim, numContours = 15):
        masked = self.getFaceImage(mapDim)
        regressionMap = None
        contours = []
        contourLengths = {}

        try:
            cellSize = 1 / mapDim
            regressionMap = skfmm.distance(masked, dx=cellSize) * 2
            regmax = np.amax(regressionMap)
            regressionMap = regressionMap[:, :].copy()
            regressionMap[np.where(masked == 0)] = regmax # Make the core black

            for dist in np.linspace(0, regmax, numContours):
                contours.append([])
                contourLengths[dist] = 0
                layerContours = measure.find_contours(regressionMap, dist, fully_connected='high')
                for contour in layerContours:
                    contours[-1].append(contour)
                    contourLengths[dist] += geometry.length(contour, mapDim)

        except ValueError as e: # If there aren't any contours, do nothing
            print(e)

        return (masked, regressionMap, contours, contourLengths)
