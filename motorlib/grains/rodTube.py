"""Rod and Tube submodule"""

import numpy as np
import skfmm
from skimage import measure

from ..enums.simAlertLevel import SimAlertLevel
from ..enums.simAlertType import SimAlertType
from ..grain import PerforatedGrain
from .. import geometry
from ..simResult import SimAlert
from ..properties import FloatProperty

class RodTubeGrain(PerforatedGrain):
    """Tbe rod and tube grain resembles a BATES grain except that it features a fully-uninhibited rod of propellant in
    the center of the core."""
    geomName = "Rod and Tube"
    def __init__(self):
        super().__init__()
        self.props['coreDiameter'] = FloatProperty('Core Diameter', 'm', 0, 1)
        self.props['rodDiameter'] = FloatProperty('Rod Diameter', 'm', 0, 1)
        self.props['supportDiameter'] = FloatProperty('Support Diameter', 'm', 0, 1)
        self.tubeWeb = None
        self.rodWeb = None

    def simulationSetup(self, config):
        self.tubeWeb = (self.props['diameter'].getValue() - self.props['coreDiameter'].getValue()) / 2
        self.rodWeb = (self.props['rodDiameter'].getValue() - self.props['supportDiameter'].getValue()) / 2
        self.wallWeb = max(self.tubeWeb, self.rodWeb)

    def getCorePerimeter(self, regDist):
        if regDist < self.tubeWeb:
            tubePerimeter = geometry.circlePerimeter(self.props['coreDiameter'].getValue() + (2 * regDist))
        else:
            tubePerimeter = 0
        if regDist < self.rodWeb:
            rodPerimeter = geometry.circlePerimeter(self.props['rodDiameter'].getValue() - (2 * regDist))
        else:
            rodPerimeter = 0
        return tubePerimeter + rodPerimeter

    def getFaceArea(self, regDist):
        if regDist < self.tubeWeb:
            outer = geometry.circleArea(self.props['diameter'].getValue())
            inner = geometry.circleArea(self.props['coreDiameter'].getValue() + (2 * regDist))
            tubeArea = outer - inner
        else:
            tubeArea = 0
        if regDist < self.rodWeb:
            outer = geometry.circleArea(self.props['rodDiameter'].getValue() - (2 * regDist))
            inner = geometry.circleArea(self.props['supportDiameter'].getValue())
            rodArea = outer - inner
        else:
            rodArea = 0
        return tubeArea + rodArea

    def getDetailsString(self, lengthUnit='m'):
        return 'Length: {}, Core: {}, Rod: {}'.format(self.props['length'].dispFormat(lengthUnit),
                                                      self.props['coreDiameter'].dispFormat(lengthUnit),
                                                      self.props['rodDiameter'].dispFormat(lengthUnit))

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['coreDiameter'].getValue() == 0:
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self.props['coreDiameter'].getValue() >= self.props['diameter'].getValue():
            aText = 'Core diameter must be less than grain diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))
        if self.props['rodDiameter'].getValue() >= self.props['coreDiameter'].getValue():
            aText = 'Rod diameter must be less than core diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText))
        return errors

    # These two functions have a lot of code reuse, but it is worth it because making this an fmmGrain would make it
    # signficantly way slower
    def getFaceImage(self, mapDim):
        # Normalize core and rod diameters
        coreRadius = (self.props['coreDiameter'].getValue() / (0.5 * self.props['diameter'].getValue())) / 2
        rodRadius = (self.props['rodDiameter'].getValue() / (0.5 * self.props['diameter'].getValue())) / 2
        supportRadius = (self.props['supportDiameter'].getValue() / (0.5 * self.props['diameter'].getValue())) / 2

        mapX, mapY = np.meshgrid(np.linspace(-1, 1, mapDim), np.linspace(-1, 1, mapDim))
        mask = np.logical_or(mapX**2 + mapY**2 > 1, mapX**2 + mapY**2 < supportRadius ** 2)
        coreMap = np.ones_like(mapX)

        # Open up core
        coreMap[mapX ** 2 + mapY ** 2 < coreRadius ** 2] = 0
        coreMap[mapX ** 2 + mapY ** 2 < rodRadius ** 2] = 1
        coreMap[mapX ** 2 + mapY ** 2 < supportRadius ** 2] = 0

        maskedMap = np.ma.MaskedArray(coreMap, mask)

        return maskedMap

    def getRegressionData(self, mapDim, numContours=15, coreBlack=True):
        masked = self.getFaceImage(mapDim)
        regressionMap = None
        contours = []
        contourLengths = {}

        try:
            cellSize = 1 / mapDim
            regressionMap = skfmm.distance(masked, dx=cellSize) * 2
            regmax = np.amax(regressionMap)
            regressionMap = regressionMap[:, :].copy()
            if coreBlack:
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
