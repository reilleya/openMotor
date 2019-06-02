from PyQt5.QtCore import QObject, pyqtSignal
from motorlib import propertyCollection, floatProperty, intProperty, enumProperty
from motorlib import unitLabels, getAllConversions


class Preferences():
    def __init__(self, propDict=None):
        self.general = propertyCollection()
        self.general.props['burnoutWebThres'] = floatProperty('Web Burnout Threshold', 'm', 2.54e-5, 3.175e-3)
        self.general.props['burnoutThrustThres'] = floatProperty('Thrust Burnout Threshold', '%', 0.01, 10)
        self.general.props['timestep'] = floatProperty('Simulation Timestep', 's', 0.0001, 0.1)
        self.general.props['ambPressure'] = floatProperty('Ambient Pressure', 'Pa', 0.0001, 102000)
        self.general.props['mapDim'] = intProperty('Grain Map Dimension', '', 250, 2000)
        self.units = propertyCollection()
        for unit in unitLabels:
            self.units.props[unit] = enumProperty(unitLabels[unit], getAllConversions(unit))

        if propDict is not None:
            self.applyDict(propDict)

    def getDict(self):
        prefDict = {}
        prefDict['general'] = self.general.getProperties()
        prefDict['units'] = self.units.getProperties()
        return prefDict

    def applyDict(self, dictionary):
        self.general.setProperties(dictionary['general'])
        self.units.setProperties(dictionary['units'])

    def getUnit(self, fromUnit):
        if fromUnit in self.units.props:
            return self.units.getProperty(fromUnit)
        return fromUnit


class PreferencesManager(QObject):

    preferencesChanged = pyqtSignal(object)

    def __init__(self):
        super().__init__()
