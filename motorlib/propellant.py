from . import units
from .properties import *

class propellant(propertyCollection):
    def __init__(self):
        super().__init__()
        self.props['name'] = stringProperty('Name')
        self.props['a'] = floatProperty('Burn rate Coefficient', 'm/(s*pa^n)', 0, 2)
        self.props['n'] = floatProperty('Burn rate Exponent', '', 0, 1)
        self.props['density'] = floatProperty('Density', 'kg/m^3', 0, 10000)
        self.props['k'] = floatProperty('Specific Heat Ratio', '', 0, 10)
        self.props['t'] = floatProperty('Combustion Temperature', 'k', 0, 10000)
        self.props['m'] = floatProperty('Exhaust Molar Mass', 'g/mol', 0, 100)
