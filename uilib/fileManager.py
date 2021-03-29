from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal

import motorlib

from .fileIO import saveFile, loadFile, fileTypes
from .helpers import FLAGS_NO_ICON
from .logger import logger

class FileManager(QObject):

    fileNameChanged = pyqtSignal(str, bool)
    newMotor = pyqtSignal(object)

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.fileHistory = []
        self.currentVersion = 0
        self.savedVersion = 0

        self.fileName = None

        self.newFile()

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
        msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        res = msg.exec_()
        if res == QMessageBox.Save:
            self.save()
            return True

        return res == QMessageBox.Discard

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

        originalName = motor.propellant.getProperty('name')
        # If the motor has a propellant that we don't have, add it to our library
        if originalName not in self.app.propellantManager.getNames():
            self.app.outputMessage('The propellant from the loaded motor was not in the library, so it was added as "{}"'.format(originalName),
                                   'New propellant added')
            self.app.propellantManager.propellants.append(motor.propellant)
            self.app.propellantManager.savePropellants()
            logger.log('Propellant from loaded motor added to library under original name "{}"'.format(originalName))

            return motor

        # If a propellant by the name already exists, we need to check if they are the same and change the name if not
        if motor.propellant.getProperties() == self.app.propellantManager.getPropellantByName(originalName).getProperties():
            return motor

        addedNumber = 1
        while motor.propellant.getProperty('name') + ' (' + str(addedNumber) + ')' in self.app.propellantManager.getNames():
            addedNumber += 1
        motor.propellant.setProperty('name', originalName + ' (' + str(addedNumber) + ')')
        self.app.propellantManager.propellants.append(motor.propellant)
        self.app.propellantManager.savePropellants()
        self.app.outputMessage('The propellant from the loaded motor matches an existing item in the library, but they have different properties. The propellant from the motor has been added to the library as "{}"'.format(motor.propellant.getProperty('name')),
                               'New propellant added')

        return motor
