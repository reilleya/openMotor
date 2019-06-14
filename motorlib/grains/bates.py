"""BATES submodule"""

import numpy as np
import skfmm
from skimage import measure

from ..grain import PerforatedGrain
from .. import geometry
from ..simResult import SimAlert, SimAlertLevel, SimAlertType
from ..properties import FloatProperty

class BatesGrain(PerforatedGrain):
    """The BATES grain has a simple cylindrical core. This type is not an FMM grain for performance reasons, as the
    calculations are easy enough to do manually."""
    geomName = "BATES"
    def __init__(self):
        super().__init__()
        self.props['coreDiameter'] = FloatProperty('Core Diameter', 'm', 0, 1)

    def simulationSetup(self, config):
        self.wallWeb = (self.props['diameter'].getValue() - self.props['coreDiameter'].getValue()) / 2

    def getCorePerimeter(self, regDist):
        return geometry.circlePerimeter(self.props['coreDiameter'].getValue() + (2 * regDist))

    def getFaceArea(self, regDist):
        outer = geometry.circleArea(self.props['diameter'].getValue())
        inner = geometry.circleArea(self.props['coreDiameter'].getValue() + (2 * regDist))
        return outer - inner

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
            aText = 'Core diameter must be less than grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))
        return errors

    # These two functions have a lot of code reuse, but it is worth it because making BATES an fmmGrain would make it
    # signficantly way slower
    def getFaceImage(self, mapDim):
        mapX, mapY = np.meshgrid(np.linspace(-1, 1, mapDim), np.linspace(-1, 1, mapDim))
        mask = mapX**2 + mapY**2 > 1
        coreMap = np.ones_like(mapX)

        # Normalize core diameter
        coreRadius = (self.props['coreDiameter'].getValue() / (0.5 * self.props['diameter'].getValue())) / 2

        # Open up core
        coreMap[mapX**2 + mapY**2 < coreRadius**2] = 0
        maskedMap = np.ma.MaskedArray(coreMap, mask)

        return maskedMap

    def getRegressionData(self, mapDim, numContours=15):
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

        except ValueError as exc: # If there aren't any contours, do nothing
            print(exc)

        return (masked, regressionMap, contours, contourLengths)
