from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog, QAction
from PyQt5.QtCore import pyqtSignal

import motorlib

from .fileIO import saveFile, loadFile, fileTypes
from .converter import Importer, Exporter
from .converters import BurnSimImporter

class ImportExportManager(QObject):

    motorImported = pyqtSignal()
    propellantImported = pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.conversions = [BurnSimImporter(self)]
        self.preferences = None # TODO: change?

    def setPreferences(self, pref):
        self.preferences = pref

    def unsavedCheck(self):
        return self.app.fileManager.unsavedCheck()

    def startFromMotor(self, motor):
        self.app.fileManager.startFromMotor(motor)
        self.motorImported.emit()

    def getRequirement(self, req):
        if req == 'motor':
            return self.app

    def createMenus(self, importMenu, exportMenu):
        for conversion in self.conversions:
            if isinstance(conversion, Importer):
                action = QAction(conversion.name, importMenu)
                importMenu.addAction(action)
            else:
                action = QAction(conversion.name, exportMenu)
                exportMenu.addAction(action)
            action.setStatusTip(conversion.description)
            action.triggered.connect(conversion.exec)
