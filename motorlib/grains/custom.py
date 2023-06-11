"""Custom Grain submodule"""

import skimage.draw as draw

from ..enums.simAlertLevel import SimAlertLevel
from ..enums.simAlertType import SimAlertType
from ..enums.units.lengthUnit import LengthUnit
from ..grain import FmmGrain
from ..properties import PolygonProperty, EnumProperty
from ..simResult import SimAlert
from ..units import getAllConversions, convert

class CustomGrain(FmmGrain):
    """Custom grains can have any core shape. They define their geometry using a polygon property, which tracks a list
    of polygons that each consist of a number of points. The polygons are scaled according to user specified units and
    drawn onto the core map."""
    geomName = 'Custom Grain'
    def __init__(self):
        super().__init__()
        self.props['points'] = PolygonProperty('Core geometry')
        self.props['dxfUnit'] = EnumProperty('DXF Unit', getAllConversions(LengthUnit.METER))

    def generateCoreMap(self):
        inUnit = self.props['dxfUnit'].getValue()
        for polygon in self.props['points'].getValue():
            row = [(self.mapDim/2) + (-self.normalize(convert(p[1], inUnit, LengthUnit.METER)) * (self.mapDim/2)) for p in polygon]
            col = [(self.mapDim/2) + (self.normalize(convert(p[0], inUnit, LengthUnit.METER)) * (self.mapDim/2)) for p in polygon]
            imageRow, imageCol = draw.polygon(row, col, self.coreMap.shape)
            self.coreMap[imageRow, imageCol] = 0

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()

        if len(self.props['points'].getValue()) > 1:
            aText = 'Support for custom grains with multiple cores is experimental'
            errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.GEOMETRY, aText))

        return errors
