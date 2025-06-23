from PyQt6.QtCore import QObject, pyqtSignal

from motorlib.properties import PropertyCollection, FloatProperty, IntProperty, EnumProperty
from motorlib.units import unitLabels, getAllConversions
from motorlib.motor import MotorConfig

from .fileIO import loadFile, saveFile, getConfigPath, fileTypes
from .defaults import DEFAULT_PREFERENCES
from .widgets import preferencesMenu
from .logger import logger

class Preferences():
    def __init__(self, propDict=None):
        self.general = MotorConfig()
        self.units = PropertyCollection()
        for unit in unitLabels:
            self.units.props[unit] = EnumProperty(unitLabels[unit], getAllConversions(unit))

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

    def __init__(self, makeMenu=True):
        super().__init__()
        self.preferences = Preferences(DEFAULT_PREFERENCES)
        if makeMenu:
            self.menu = preferencesMenu.PreferencesMenu()
            self.menu.preferencesApplied.connect(self.newPreferences)
        self.loadPreferences()

    def newPreferences(self, prefDict):
        logger.log('Updating preferences')
        self.preferences.applyDict(prefDict)
        self.savePreferences()
        self.publishPreferences()

    def loadPreferences(self):
        try:
            prefDict = loadFile(getConfigPath() + 'preferences.yaml', fileTypes.PREFERENCES)
            self.preferences.applyDict(prefDict)
            self.publishPreferences()
        except FileNotFoundError:
            logger.warn('Unable to load preferences, creating new file')
            self.savePreferences()

    def savePreferences(self):
        try:
            destinationPath = getConfigPath() + 'preferences.yaml'
            logger.log('Saving preferences to "{}"'.format(destinationPath))
            saveFile(destinationPath, self.preferences.getDict(), fileTypes.PREFERENCES)
        except:
            logger.warn('Unable to save preferences')

    def showMenu(self):
        logger.log('Showing preferences menu')
        self.menu.load(self.preferences)
        self.menu.show()

    def publishPreferences(self):
        self.preferencesChanged.emit(self.preferences)
