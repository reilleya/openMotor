from .properties import *
from . import geometry
from scipy.optimize import fsolve

def eRatioFromPRatio(k, pr):
    return (((k+1)/2)**(1/(k-1))) * (pr ** (1/k)) * ((((k+1)/(k-1))*(1-(pr**((k-1)/k))))**0.5)

class nozzle(propertyCollection):
    def __init__(self):
        super().__init__()
        self.props['throat'] = floatProperty('Throat Diameter', 'm', 0, 0.5)
        self.props['exit'] = floatProperty('Exit Diameter', 'm', 0, 1)
        self.props['efficiency'] = floatProperty('Efficiency', '', 0, 2)

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Throat: ' + self.props['throat'].dispFormat(lengthUnit)

    def calcExpansion(self):
        return (self.props['exit'].getValue() / self.props['throat'].getValue()) ** 2

    def getThroatArea(self):
        return geometry.circleArea(self.props['throat'].getValue())

    def getExitArea(self):
        return geometry.circleArea(self.props['exit'].getValue())

    def getExitPressure(self, k, inputPressure):
        return fsolve(lambda x: (1/self.calcExpansion()) - eRatioFromPRatio(k, x / inputPressure), 50000)[0]
