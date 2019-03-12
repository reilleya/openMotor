from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal

from motorlib import propertyCollection, floatProperty, enumProperty
from motorlib import unitLabels, getAllConversions

class preferences():
    def __init__(self):
        self.general = propertyCollection()
        self.general.props['burnoutWebThres'] = floatProperty('Web Burnout Threshold', 'm', 2.54e-5, 3.175e-3)
        self.general.props['burnoutThrustThres'] = floatProperty('Thrust Burnout Threshold', '%', 0.01, 10)
        self.general.props['timestep'] = floatProperty('Simulation Timestep', 's', 0.0001, 0.1)
        self.general.props['ambPressure'] = floatProperty('Ambient Pressure', 'pa', 0.0001, 102000)
        self.units = propertyCollection()
        for unit in unitLabels:
            self.units.props[unit] = enumProperty(unitLabels[unit], getAllConversions(unit))

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
        else:
            return fromUnit


class PreferencesWindow(QWidget):

    preferencesApplied = pyqtSignal(dict)

    def __init__(self):
        QWidget.__init__(self)

        loadUi("resources/Preferences.ui", self)
        self.buttonBox.accepted.connect(self.apply)
        self.buttonBox.rejected.connect(self.cancel)

    def load(self, pref):
        self.settingsEditorGeneral.setPreferences(pref)
        self.settingsEditorGeneral.loadProperties(pref.general)
        self.settingsEditorUnits.loadProperties(pref.units)

    def apply(self):
        self.preferencesApplied.emit({'general': self.settingsEditorGeneral.getProperties(), 'units': self.settingsEditorUnits.getProperties()})
        self.hide()

    def cancel(self):
        self.hide()
