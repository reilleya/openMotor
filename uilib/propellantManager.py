from PyQt6.QtCore import QObject, pyqtSignal

from motorlib.propellant import Propellant

from .defaults import DEFAULT_PROPELLANTS
from .fileIO import fileTypes, getConfigPath, loadFile, saveFile
from .logger import logger
from .widgets.propellantMenu import PropellantMenu


class PropellantManager(QObject):

    updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.propellants = []
        self.loadPropellants()

        self.propMenu = PropellantMenu(self)
        self.propMenu.closed.connect(self.updated.emit)

    def loadPropellants(self):
        try:
            propList = loadFile(getConfigPath() + 'propellants.yaml', fileTypes.PROPELLANTS)
            for propDict in propList:
                newProp = Propellant()
                newProp.setProperties(propDict)
                self.propellants.append(newProp)
        except FileNotFoundError:
            logger.warn('No propellant file found, saving defaults')
            self.propellants = [Propellant(prop) for prop in DEFAULT_PROPELLANTS]
            self.savePropellants()

    def savePropellants(self):
        propellants = [prop.getProperties() for prop in self.propellants]
        try:
            destinationPath = getConfigPath() + 'propellants.yaml'
            logger.log('Saving propellants to "{}"'.format(destinationPath))
            saveFile(destinationPath, propellants, fileTypes.PROPELLANTS)
        except:
            logger.warn('Unable to save propellants!')

    def getNames(self):
        return [prop.getProperty('name') for prop in self.propellants]

    def getPropellantByName(self, name):
        return self.propellants[self.getNames().index(name)]

    def showMenu(self):
        logger.log('Showing propellant menu')
        self.propMenu.setupPropList()
        self.propMenu.show()

    def setPreferences(self, pref):
        self.propMenu.ui.propEditor.setPreferences(pref)
