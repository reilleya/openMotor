"""Propellant submodule that contains the propellant class."""

from .properties import PropertyCollection, FloatProperty, StringProperty

class Propellant(PropertyCollection):
    """Contains the physical and thermodynamic properties of a propellant formula."""
    def __init__(self, propDict=None):
        super().__init__()
        self.props['name'] = StringProperty('Name')
        self.props['a'] = FloatProperty('Burn rate Coefficient', 'm/(s*Pa^n)', 0, 2)
        self.props['n'] = FloatProperty('Burn rate Exponent', '', 0, 1)
        self.props['density'] = FloatProperty('Density', 'kg/m^3', 0, 10000)
        self.props['k'] = FloatProperty('Specific Heat Ratio', '', 1+1e-6, 10)
        self.props['t'] = FloatProperty('Combustion Temperature', 'K', 0, 10000)
        self.props['m'] = FloatProperty('Exhaust Molar Mass', 'g/mol', 1e-6, 100)

        if propDict is not None:
            self.setProperties(propDict)

    def getCStar(self):
        """Returns the propellant's characteristic velocity."""
        gamma = self.props['k'].getValue()
        temp = self.props['t'].getValue()
        molarMass = self.props['m'].getValue()
        gasConst = 8314
        num = (gamma * gasConst/molarMass * temp)**0.5
        denom = gamma * ((2/(gamma+1))**((gamma+1)/(gamma-1)))**0.5
        return num / denom
