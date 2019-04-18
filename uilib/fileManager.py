from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from . import defaults, saveFile, loadFile, fileTypes
import motorlib
import yaml

class fileManager(QObject):

    fileNameChanged = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()

        self.fileHistory = []
        self.currentVersion = 0
        self.savedVersion = 0

        self.fileName = None

        self.newFile()

    def newFile(self):
        if self.unsavedCheck():
            self.fileHistory = [defaults.defaultMotor().getDict()]
            self.currentVersion = 0
            self.savedVersion = 0
            self.fileName = None
            self.sendTitleUpdate()

    def save(self):
        if self.fileName is None:
            self.saveAs()
        else:
            try:
                saveFile(self.fileName, self.fileHistory[self.currentVersion], fileTypes.MOTOR)
                self.savedVersion = self.currentVersion
                self.sendTitleUpdate()
            except Exception as e:
                self.showException(e)

    def saveAs(self):
        fn = self.showSaveDialog()
        if fn is not None:
            self.fileName = fn
            self.save()

    def load(self, path = None):
        if self.unsavedCheck():
            if path is None:
                path = QFileDialog.getOpenFileName(None, 'Load motor', '', 'Motor Files (*.ric)')[0]
            if path != '': # If they cancel the dialog, path will be an empty string
                try:
                    res = loadFile(path, fileTypes.MOTOR)
                    if res is not None:
                        self.fileHistory = [res]
                        self.currentVersion = 0
                        self.savedVersion = 0
                        self.fileName = path
                        self.sendTitleUpdate()
                        return True
                except Exception as e:
                    self.showException(e)

        return False # If no file is loaded, return false

    def showException(self, exception):
        msg = QMessageBox()
        msg.setText("An error occured accessing the file:")
        msg.setInformativeText(str(exception))
        msg.setWindowTitle("Error")
        msg.exec_()

    def getCurrentMotor(self):
        nm = motorlib.motor()
        nm.loadDict(self.fileHistory[self.currentVersion])
        return nm

    def addNewMotorHistory(self, motor): # Add a new version of the motor to the motor history. Should be used for all user interactions.
        if motor.getDict() != self.fileHistory[self.currentVersion]:
            if self.canRedo():
                del self.fileHistory[self.currentVersion + 1:]
            self.fileHistory.append(motor.getDict())
            self.currentVersion += 1
            self.sendTitleUpdate()

    def overrideCurrentMotor(self, motor): # Changes the current motor without adding undo history. Should not be used after user interaction.
        self.fileHistory[-1] = motor.getDict()

    def canUndo(self):
        return self.currentVersion > 0

    def undo(self):
        if self.canUndo():
            self.currentVersion -= 1
            self.sendTitleUpdate()

    def canRedo(self):
        return self.currentVersion < len(self.fileHistory) - 1

    def redo(self):
        if self.canRedo():
            self.currentVersion += 1
            self.sendTitleUpdate()

    def unsavedCheck(self):
        if self.savedVersion != self.currentVersion:
            msg = QMessageBox()

            msg.setText("The current file has unsaved changes. Close without saving?")
            msg.setWindowTitle("Close without saving?")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            res = msg.exec_()
            if res == QMessageBox.Save:
                self.save()
                return True
            elif res == QMessageBox.Discard:
                return True
            else:
                return False

        return True

    def sendTitleUpdate(self):
        self.fileNameChanged.emit(self.fileName, self.savedVersion == self.currentVersion)

    def showSaveDialog(self):
        path = QFileDialog.getSaveFileName(None, 'Save motor', '', 'Motor Files (*.ric)')[0]
        if path == '' or path is None:
            return
        if path[-4:] != '.ric':
            path += '.ric'
        return path
