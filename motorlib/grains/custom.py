from .. import fmmGrain
from ..properties import *
from .. import simAlert, simAlertLevel, simAlertType

import numpy as np
import skimage.draw as draw

class CustomGrain(fmmGrain):
    geomName = 'Custom Grain'
    def __init__(self):
        super().__init__()
        self.props['points'] = polygonProperty('Core geometry')

    def generateCoreMap(self):
        for polygon in self.props['points'].getValue():
            r = [self.mapDim - (self.normalize(p[1])  * (self.mapDim / 2)) for p in polygon]
            c = [self.normalize(p[0]) * (self.mapDim / 2) for p in polygon]
            rr, cc = draw.polygon(r, c)
            self.coreMap[rr, cc] = 0

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if len(self.props['points'].getValue()) > 1:
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Support for custom grains with multiple cores is experimental'))

        return errors
