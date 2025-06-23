from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QAction

import os
import motorlib

from .fileIO import saveFile, loadFile, fileTypes, getConfigPath
from .helpers import FLAGS_NO_ICON, excludeKeys
from .logger import logger

class FileManager(QObject):

    MAX_RECENT_FILES = 5

    fileNameChanged = pyqtSignal(str, bool)
    newMotor = pyqtSignal(object)
    # TODO: eventually a signal like this that makes the mainWindow repopulate the propellant editor should
    # be emitted whenever load() is called
    recentFileLoaded = pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.fileHistory = []
        self.currentVersion = 0
        self.savedVersion = 0

        self.fileName = None

        self.newFile()

        self.recentlyOpenedMenu = None
        self.recentlyOpenedFiles = []
        self.recentFilesPath = os.path.join(getConfigPath(), 'recent_files.yaml')

        self.loadRecentlyOpenedFilesList()

    # Check if current motor is unsaved and start over from default motor. Called when the menu item is triggered.
    def newFile(self):
        if not self.unsavedCheck():
            logger.log('Cannot start new file because of existing one')
            return
        logger.log('Starting new motor file')
        newMotor = motorlib.motor.Motor()
        motorConfig = self.app.preferencesManager.preferences.general.getProperties()
        newMotor.config.setProperties(motorConfig) # Copy over user's preferences
        self.startFromMotor(newMotor)

    # Reset to empty motor history and set current motor to what is passed in
    def startFromMotor(self, motor, filename=None):
        motor = self.checkPropellant(motor)
        self.fileHistory = [motor.getDict()]
        self.currentVersion = 0
        self.savedVersion = 0
        self.fileName = filename
        self.sendTitleUpdate()
        self.newMotor.emit(motor)

    # Asks the user for a filename if they haven't provided one. Otherwise, dump the motor to a file and show any
    # resulting errors in a popup. Called when the menu item is triggered.
    def save(self):
        if self.fileName is None:
            # Though this function calls save again, the above condition will be false on the second time around
            # and the file will save
            self.saveAs()
        else:
            try:
                saveFile(self.fileName, self.fileHistory[self.currentVersion], fileTypes.MOTOR)
                self.savedVersion = self.currentVersion
                self.sendTitleUpdate()
            except Exception as exc:
                self.app.outputException(exc, "An error occurred while saving the file: ")

    # Asks for a new file name and saves the motor
    def saveAs(self):
        fileName = self.showSaveDialog()
        if fileName is not None:
            self.fileName = fileName
            self.save()
            self.addRecentFile(fileName)

    # Checks for unsaved changes, asks for a filename, and loads the file
    def load(self, path=None):
        if self.unsavedCheck():
            if path is None:
                path = QFileDialog.getOpenFileName(None, 'Load motor', '', 'Motor Files (*.ric)')[0]
            if path != '': # If they cancel the dialog, path will be an empty string
                try:
                    res = loadFile(path, fileTypes.MOTOR)
                    if res is not None:
                        motor = motorlib.motor.Motor()
                        motor.applyDict(res)
                        self.startFromMotor(motor, path)
                        self.addRecentFile(path)
                        return True
                except Exception as exc:
                    self.app.outputException(exc, "An error occurred while loading the file: ")

        return False # If no file is loaded, return false

    # Return the recent end of the motor history
    def getCurrentMotor(self):
        newMotor = motorlib.motor.Motor()
        newMotor.applyDict(self.fileHistory[self.currentVersion])
        return newMotor

    # Add a new version of the motor to the motor history. Should be used for all user interactions.
    def addNewMotorHistory(self, motor):
        if motor.getDict() != self.fileHistory[self.currentVersion]:
            if self.canRedo():
                del self.fileHistory[self.currentVersion + 1:]
            self.fileHistory.append(motor.getDict())
            self.currentVersion += 1
            self.sendTitleUpdate()
            self.newMotor.emit(motor)

    # Updates the propellant of all motors in the history to match the current values in the manager without adding any
    # new history
    def updatePropellant(self):
        logger.log('Propellant for current motor changed, updating all copies in history')
        for motor in self.fileHistory:
            if motor['propellant'] is not None:
                if motor['propellant']['name'] in self.app.propellantManager.getNames():
                    prop = self.app.propellantManager.getPropellantByName(motor['propellant']['name']).getProperties()
                    motor['propellant'] = prop
                else:
                    motor['propellant'] = None

    # Returns true if there is history before the current motor
    def canUndo(self):
        return self.currentVersion > 0

    # Rolls back the current motor to point at the motor before it in the history
    def undo(self):
        if not self.canUndo():
            logger.log('Nothing to undo')
            return

        logger.log('Applying undo')
        self.currentVersion -= 1
        self.sendTitleUpdate()
        self.newMotor.emit(self.getCurrentMotor())

    # Returns true if there is history ahead of the current motor
    def canRedo(self):
        return self.currentVersion < len(self.fileHistory) - 1

    # Changes current motor to be the next motor in history
    def redo(self):
        if not self.canRedo():
            logger.log('Nothing to redo')
            return

        logger.log('Applying redo')
        self.currentVersion += 1
        self.sendTitleUpdate()
        self.newMotor.emit(self.getCurrentMotor())

    # If there is unsaved history, ask the user if they want to save it. Returns true if it is safe to exit or start a
    # new motor (save, discard) or false if not (cancel)
    def unsavedCheck(self):
        if self.savedVersion == self.currentVersion:
            return True

        msg = QMessageBox()

        msg.setWindowFlags(FLAGS_NO_ICON)
        msg.setText("The current file has unsaved changes. Close without saving?")
        msg.setWindowTitle("Close without saving?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )

        res = msg.exec()
        if res == QMessageBox.StandardButton.Save:
            self.save()
            return True

        return res == QMessageBox.StandardButton.Discard

    # Outputs the filename component of the title
    def sendTitleUpdate(self):
        self.fileNameChanged.emit(self.fileName, self.savedVersion == self.currentVersion)

    # Pops up a save file dialog and returns the path, or None if it is canceled
    def showSaveDialog(self):
        path = QFileDialog.getSaveFileName(None, 'Save motor', '', 'Motor Files (*.ric)')[0]
        if path == '' or path is None:
            return None

        if path[-4:] != '.ric':
            path += '.ric'

        return path

    # Checks if a motor's propellant is in the library, adds it if it isn't, and also looks for conflicts
    def checkPropellant(self, motor):
        # If the motor doesn't have a propellant set, there's nothing to do
        if motor.propellant is None:
            return motor

        propManager = self.app.propellantManager
        originalName = motor.propellant.getProperty('name')
        # If the motor has a propellant that we don't have, add it to our library
        if originalName not in propManager.getNames():
            # Check if any propellants in the library have the same properties and offer to dedupe
            for libraryPropellantName in propManager.getNames():
                libraryProperties = excludeKeys(propManager.getPropellantByName(libraryPropellantName).getProperties(), ['name'])
                motorProperties = excludeKeys(motor.propellant.getProperties(), ['name'])
                if libraryProperties == motorProperties:
                    message = 'The propellant from the loaded motor ("{}") was not in the library, but the properties match "{}" from the library. Should the loaded motor be updated to use this propellant?'
                    shouldDeDupe = self.app.promptYesNo(message.format(motor.propellant.getProperty('name'), libraryPropellantName))
                    if shouldDeDupe:
                        motor.propellant.setProperty('name', libraryPropellantName)
                        return motor

            self.app.outputMessage('The propellant from the loaded motor was not in the library, so it was added as "{}"'.format(originalName),
                                   'New propellant added')
            propManager.propellants.append(motor.propellant)
            propManager.savePropellants()
            logger.log('Propellant from loaded motor added to library under original name "{}"'.format(originalName))

            return motor

        addedNumber = 0
        name = originalName
        while name in propManager.getNames():
            existingProps = excludeKeys(propManager.getPropellantByName(name).getProperties(), ['name'])
            motorProps = excludeKeys(motor.propellant.getProperties(), ['name'])
            if existingProps == motorProps:
                # If this isn't the first loop, we need to change the name to add the number
                if addedNumber != 0:
                    motor.propellant.setProperty('name', name)
                    message = 'Propellant from loaded motor has the same name as one in the library ("{}"), but their properties do not match. It does match "{}", so it has been updated to that propellant.'.format(originalName, name)
                    self.app.outputMessage(message)
                return motor
            addedNumber += 1
            name = '{} ({})'.format(originalName, addedNumber)
        motor.propellant.setProperty('name', '{} ({})'.format(originalName, addedNumber))
        propManager.propellants.append(motor.propellant)
        propManager.savePropellants()
        self.app.outputMessage('The propellant from the loaded motor matches an existing item in the library, but they have different properties. The propellant from the motor has been added to the library as "{}"'.format(motor.propellant.getProperty('name')),
                               'New propellant added')

        return motor

    def loadRecentlyOpenedFilesList(self):
        try:
            self.recentFilesList = loadFile(self.recentFilesPath, fileTypes.RECENT_FILES)['recentFilesList']
        except FileNotFoundError:
            logger.warn('Unable to load recent files, creating new file at {}'.format(self.recentFilesPath))
            self.recentFilesList = []
            saveFile(self.recentFilesPath, {'recentFilesList': self.recentFilesList}, fileTypes.RECENT_FILES)

    def createRecentlyOpenedMenu(self, recentlyOpenedMenu):
        self.recentlyOpenedMenu = recentlyOpenedMenu
        self.loadRecentlyOpenedFilesList()
        self.createRecentlyOpenedItems()

    def createRecentlyOpenedItems(self):
        if self.recentlyOpenedMenu is None:
            return

        self.recentlyOpenedMenu.clear()

        if len(self.recentFilesList) == 0:
            self.recentlyOpenedMenu.addAction(QAction('No Recent Files', self.recentlyOpenedMenu))
            return

        for filepath in self.recentFilesList:
            _, filename = os.path.split(filepath)
            action = QAction(filename, self.recentlyOpenedMenu)
            action.triggered.connect(lambda _, path=filepath: self.loadRecentFile(path))
            self.recentlyOpenedMenu.addAction(action)

    def loadRecentFile(self, path):
        self.load(path)
        self.recentFileLoaded.emit()

    def addRecentFile(self, filepath):
        if filepath in self.recentFilesList:
            self.recentFilesList.remove(filepath)

        self.recentFilesList = [filepath] + self.recentFilesList

        self.recentFilesList = self.recentFilesList[:FileManager.MAX_RECENT_FILES]

        saveFile(self.recentFilesPath, {'recentFilesList': self.recentFilesList}, fileTypes.RECENT_FILES)

        self.createRecentlyOpenedItems()
