from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from motorlib import propertyCollection, floatProperty, enumProperty
from motorlib import unitLabels, getAllConversions

class preferences():
    def __init__(self):
        self.general = propertyCollection()
        self.general.props['burnoutThres'] = floatProperty('Burnout Threshold', 'm', 2.54e-5, 3.175e-3)
        self.general.props['timestep'] = floatProperty('Simulation Timestep', 's', 0.0001, 0.1)
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

class PreferencesWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.p = preferences()

        loadUi("Preferences.ui", self)
        self.buttonBox.accepted.connect(self.apply)
        self.buttonBox.rejected.connect(self.cancel)

        self.settingsEditorGeneral.loadProperties(self.p.general)
        self.settingsEditorUnits.loadProperties(self.p.units)

    def apply(self):
        self.hide()

    def cancel(self):
        self.hide()
