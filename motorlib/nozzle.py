from .properties import *
from . import geometry

class nozzle(propertyCollection):
    def __init__(self):
        super().__init__()
        self.props['throat'] = floatProperty('Throat Diameter', 'm', 0, 100)
        self.props['exit'] = floatProperty('Exit Diameter', 'm', 0, 100)

    def getDetailsString(self):
        return 'Throat: ' + self.props['throat'].dispFormat('in')

    def calcExpansion(self):
        return (self.props['exit'].getValue() / self.props['throat'].getValue()) ** 2

    def getThroatArea(self):
        return geometry.circleArea(self.props['throat'].getValue())

    def getExitArea(self):
        return geometry.circleArea(self.props['exit'].getValue())