from . import units
from .properties import *

class Propellant(propertyCollection):
    def __init__(self, propDict = None):
        super().__init__()
        self.props['name'] = stringProperty('Name')
        self.props['a'] = floatProperty('Burn rate Coefficient', 'm/(s*Pa^n)', 0, 2)
        self.props['n'] = floatProperty('Burn rate Exponent', '', 0, 1)
        self.props['density'] = floatProperty('Density', 'kg/m^3', 0, 10000)
        self.props['k'] = floatProperty('Specific Heat Ratio', '', 1+1e-6, 10)
        self.props['t'] = floatProperty('Combustion Temperature', 'K', 0, 10000)
        self.props['m'] = floatProperty('Exhaust Molar Mass', 'g/mol', 1e-6, 100)

        if propDict is not None:
            self.setProperties(propDict)

    def getCStar(self):
        k = self.props['k'].getValue()
        t = self.props['t'].getValue()
        m = self.props['m'].getValue()
        r = 8314
        num = (k * r/m * t)**0.5
        denom = k * ((2/(k+1))**((k+1)/(k-1)))**0.5
        return num / denom
