"""Propellant submodule that contains the propellant class."""

from scipy.optimize import fsolve

from .properties import PropertyCollection, FloatProperty, StringProperty, TabularProperty
from .simResult import SimAlert, SimAlertLevel, SimAlertType
from .constants import gasConstant

class PropellantTab(PropertyCollection):
    """Contains the combustion properties of a propellant over a specified pressure range."""
    def __init__(self, tabDict=None):
        super().__init__()
        self.props['minPressure'] = FloatProperty('Minimum Pressure', 'Pa', 0, 7e7)
        self.props['maxPressure'] = FloatProperty('Maximum Pressure', 'Pa', 0, 7e7)
        self.props['a'] = FloatProperty('Burn rate Coefficient', 'm/(s*Pa^n)', 1E-8, 2)
        self.props['n'] = FloatProperty('Burn rate Exponent', '', -0.99, 0.99)
        self.props['k'] = FloatProperty('Specific Heat Ratio', '', 1+1e-6, 10)
        self.props['t'] = FloatProperty('Combustion Temperature', 'K', 1, 10000)
        self.props['m'] = FloatProperty('Exhaust Molar Mass', 'g/mol', 1e-6, 100)
        if tabDict is not None:
            self.setProperties(tabDict)


class Propellant(PropertyCollection):
    """Contains the physical and thermodynamic properties of a propellant formula."""
    def __init__(self, propDict=None):
        super().__init__()
        self.props['name'] = StringProperty('Name')
        self.props['density'] = FloatProperty('Density', 'kg/m^3', 1, 10000)
        self.props['tabs'] = TabularProperty('Properties', PropellantTab)
        if propDict is not None:
            self.setProperties(propDict)

    def getCStar(self, pressure):
        """Returns the propellant's characteristic velocity."""
        _, _, gamma, temp, molarMass = self.getCombustionProperties(pressure)
        num = (gamma * gasConstant / molarMass * temp)**0.5
        denom = gamma * ((2 / (gamma + 1))**((gamma + 1) / (gamma - 1)))**0.5
        return num / denom

    def getBurnRate(self, pressure):
        """Returns the propellant's burn rate for the given pressure"""
        ballA, ballN, _, _, _ = self.getCombustionProperties(pressure)
        return ballA * (pressure ** ballN)

    def getPressureFromKn(self, kn):
        density = self.getProperty('density')
        tabPressures = []
        for tab in self.getProperty('tabs'):
            ballA, ballN, gamma, temp, molarMass = tab['a'], tab['n'], tab['k'], tab['t'], tab['m']
            num = kn * density * ballA
            exponent = 1 / (1 - ballN)
            denom = ((gamma / ((gasConstant / molarMass) * temp)) * ((2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1)))) ** 0.5
            tabPressure = (num / denom) ** exponent
            # If the pressure that a burnrate produces falls into its range, we know it is the proper burnrate
            # Due to floating point error, we sometimes get a situation in which no burnrate produces the proper pressure
            # For this scenario, we go by whichever produces the least error
            minTabPressure = tab['minPressure']
            maxTabPressure = tab['maxPressure']
            if minTabPressure == self.getMinimumValidPressure() and tabPressure < maxTabPressure:
                return tabPressure
            if maxTabPressure == self.getMaximumValidPressure() and minTabPressure < tabPressure:
                return tabPressure
            if minTabPressure < tabPressure < maxTabPressure:
                return tabPressure
            tabPressures.append([min(abs(minTabPressure - tabPressure), abs(tabPressure - maxTabPressure)), tabPressure])

        tabPressures.sort(key=lambda x: x[0]) # Sort by the pressure error
        return tabPressures[0][1] # Return the pressure

    def getKnFromPressure(self, pressure):
        func = lambda kn: self.getPressureFromKn(kn) - pressure

        return fsolve(func, [250], maxfev=1000)

    def getCombustionProperties(self, pressure):
        """Returns the propellant's a, n, gamma, combustion temp and molar mass for a given pressure"""
        closest = {}
        closestPressure = 1e100
        for tab in self.getProperty('tabs'):
            if tab['minPressure'] < pressure < tab['maxPressure']:
                return tab['a'], tab['n'], tab['k'], tab['t'], tab['m']
            if abs(pressure - tab['minPressure']) < closestPressure:
                closest = tab
                closestPressure = abs(pressure - tab['minPressure'])
            if abs(pressure - tab['maxPressure']) < closestPressure:
                closest = tab
                closestPressure = abs(pressure - tab['maxPressure'])

        return closest['a'], closest['n'], closest['k'], closest['t'], closest['m']

    def getMinimumValidPressure(self):
        """Returns the lowest pressure value with associated combustion properties"""
        return min([tab['minPressure'] for tab in self.getProperty('tabs')])

    def getMaximumValidPressure(self):
        """Returns the highest pressure value with associated combustion properties"""
        return max([tab['maxPressure'] for tab in self.getProperty('tabs')])

    def getErrors(self):
        """Checks that all tabs have smaller start pressures than their end pressures, and verifies that no ranges
        overlap."""
        errors = []
        for tabId, tab in enumerate(self.getProperty('tabs')):
            if tab['maxPressure'] == tab['minPressure']:
                errText = 'Tab #{} has the same minimum and maximum pressures.'.format(tabId + 1)
                errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, errText, 'Propellant'))
            if tab['maxPressure'] < tab['minPressure']:
                errText = 'Tab #{} has reversed pressure limits.'.format(tabId + 1)
                errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, errText, 'Propellant'))
            for otherTabId, otherTab in enumerate(self.getProperty('tabs')):
                if tabId != otherTabId:
                    if otherTab['minPressure'] < tab['maxPressure'] < otherTab['maxPressure']:
                        err = 'Tabs #{} and #{} have overlapping ranges.'.format(tabId + 1, otherTabId + 1)
                        errors.append(SimAlert(SimAlertLevel.ERROR, SimAlertType.VALUE, err, 'Propellant'))
        return errors

    def getPressureErrors(self, pressure):
        """Returns if the propellant has any errors associated with the supplied pressure such as not having set
        combustion properties"""
        errors = []
        for tab in self.getProperty('tabs'):
            if tab['minPressure'] < pressure < tab['maxPressure']:
                return errors
        aText = "Chamber pressure deviated from propellant's entered ranges. Results may not be accurate."
        errors.append(SimAlert(SimAlertLevel.WARNING, SimAlertType.VALUE, aText, 'Propellant'))
        return errors

    def addTab(self, tab):
        """Adds a set of combustion properties to the propellant"""
        self.props['tabs'].addTab(tab)
