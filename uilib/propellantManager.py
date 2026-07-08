from os.path import join
from os import replace

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

import motorlib

from .defaults import DEFAULT_PROPELLANTS
from .fileIO import loadFile, saveFile, fileTypes, getConfigPath
from .widgets.propellantMenu import PropellantMenu
from .logger import logger

class PropellantManager(QObject):

    updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.propellants = []
        self.loadPropellants()

        self.propMenu = PropellantMenu(self)
        self.propMenu.closed.connect(self.updated.emit)

    def loadPropellants(self):
        propellantsPath = join(getConfigPath(), 'propellants.yaml')
        try:
            propList = loadFile(getConfigPath() + 'propellants.yaml', fileTypes.PROPELLANTS)
            for propDict in propList:
                newProp = motorlib.propellant.Propellant()
                newProp.setProperties(propDict)
                self.propellants.append(newProp)
        except FileNotFoundError:
            logger.warn('No propellant file found, saving defaults')
            self.propellants = [motorlib.propellant.Propellant(prop) for prop in DEFAULT_PROPELLANTS]
            self.savePropellants()
        except Exception as error:
            backupPath = join(getConfigPath(), 'propellants_backup.yaml')
            logger.warn('Error loading propellants: {}'.format(error))
            QApplication.instance().outputException(error, "Failed to load propellants. Backing up file to '{}' and starting fresh.".format(backupPath))
            replace(propellantsPath, backupPath)
            self.propellants = [motorlib.propellant.Propellant(prop) for prop in DEFAULT_PROPELLANTS]
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

    # Modifies a propellant's name to not collide with any existing propellants, if necessary
    def getUniquePropellantName(self, name):
        if name not in self.getNames():
            return name
        withNumber = "{} ({})"
        number = 1
        while withNumber.format(name, number) in self.getNames():
            number += 1
        return withNumber.format(name, number)

    def showMenu(self):
        logger.log('Showing propellant menu')
        self.propMenu.setupPropList()
        self.propMenu.show()

    def setPreferences(self, pref):
        self.propMenu.ui.propEditor.setPreferences(pref)
