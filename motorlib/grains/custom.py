from .. import fmmGrain
from ..properties import *
from .. import simAlert, simAlertLevel, simAlertType
from ..units import getAllConversions, convert

import numpy as np
import skimage.draw as draw

class CustomGrain(fmmGrain):
    geomName = 'Custom Grain'
    def __init__(self):
        super().__init__()
        self.props['points'] = polygonProperty('Core geometry')
        self.props['dxfUnit'] = enumProperty('DXF Unit', getAllConversions('m'))

    def generateCoreMap(self):
        inUnit = self.props['dxfUnit'].getValue()
        for polygon in self.props['points'].getValue():
            r = [(self.mapDim / 2) + (-self.normalize(convert(p[1], inUnit, 'm')) * (self.mapDim / 2)) for p in polygon]
            c = [(self.mapDim / 2) + (self.normalize(convert(p[0], inUnit, 'm')) * (self.mapDim / 2)) for p in polygon]
            rr, cc = draw.polygon(r, c, self.coreMap.shape)
            self.coreMap[rr, cc] = 0

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if len(self.props['points'].getValue()) > 1:
            errors.append(simAlert(simAlertLevel.WARNING, simAlertType.GEOMETRY, 'Support for custom grains with multiple cores is experimental'))

        return errors
