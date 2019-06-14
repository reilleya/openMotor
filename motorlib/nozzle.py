"""This submodule houses the nozzle object and functions related to isentropic flow"""

from scipy.optimize import fsolve

from .properties import FloatProperty, PropertyCollection
from . import geometry
from .simResult import SimAlert, SimAlertLevel, SimAlertType


def eRatioFromPRatio(k, pRatio):
    """Returns the expansion ratio of a nozzle given the pressure ratio it causes."""
    return (((k+1)/2)**(1/(k-1))) * (pRatio ** (1/k)) * ((((k+1)/(k-1))*(1-(pRatio**((k-1)/k))))**0.5)

class Nozzle(PropertyCollection):
    """An object that contains the details about a motor's nozzle."""
    def __init__(self):
        super().__init__()
        self.props['throat'] = FloatProperty('Throat Diameter', 'm', 0, 0.5)
        self.props['exit'] = FloatProperty('Exit Diameter', 'm', 0, 1)
        self.props['efficiency'] = FloatProperty('Efficiency', '', 0, 2)

    def getDetailsString(self, preferences):
        """Returns a human-readable string containing some details about the nozzle."""
        lengthUnit = preferences.units.getProperty('m')
        return 'Throat: ' + self.props['throat'].dispFormat(lengthUnit)

    def calcExpansion(self):
        """Returns the nozzle's expansion ratio."""
        return (self.props['exit'].getValue() / self.props['throat'].getValue()) ** 2

    def getThroatArea(self):
        """Returns the area of the nozzle's throat."""
        return geometry.circleArea(self.props['throat'].getValue())

    def getExitArea(self):
        """Return the area of the nozzle's exit."""
        return geometry.circleArea(self.props['exit'].getValue())

    def getExitPressure(self, k, inputPressure):
        """Solves for the nozzle's exit pressure, given an input pressure and the gas's specific heat ratio."""
        return fsolve(lambda x: (1/self.calcExpansion()) - eRatioFromPRatio(k, x / inputPressure), 0)[0]

    def getGeometryErrors(self):
        """Returns a list containing any errors with the nozzle's properties."""
        errors = []
        if self.props['throat'].getValue() == 0:
            aText = 'Throat diameter must not be 0'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText, 'Nozzle'))
        if self.props['exit'].getValue() < self.props['throat'].getValue():
            aText = 'Exit diameter must not be smaller than throat diameter'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.GEOMETRY, aText, 'Nozzle'))
        if self.props['efficiency'].getValue() == 0:
            aText = 'Efficiency must not be 0'
            errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.CONSTRAINT, aText, 'Nozzle'))
        return errors
