import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

import motorlib
from uilib import preferencesManager, propellantManager, simulationManager, fileManager, toolManager
from uilib import importExportManager
import uilib.widgets.mainWindow

class App(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.headless = '-h' in args

        self.preferencesManager = uilib.preferencesManager.PreferencesManager()

        self.propellantManager = uilib.propellantManager.PropellantManager()
        self.preferencesManager.preferencesChanged.connect(self.propellantManager.setPreferences)

        self.simulationManager = uilib.simulationManager.SimulationManager()
        self.preferencesManager.preferencesChanged.connect(self.simulationManager.setPreferences)

        self.fileManager = uilib.fileManager.FileManager(self)
        startupFileLoaded = False
        if len(args) > 1 and args[-1][0] != '-':
            startupFileLoaded = self.fileManager.load(args[-1])

        self.toolManager = uilib.toolManager.ToolManager(self)
        self.preferencesManager.preferencesChanged.connect(self.toolManager.setPreferences)

        self.importExportManager = uilib.importExportManager.ImportExportManager(self)
        self.preferencesManager.preferencesChanged.connect(self.importExportManager.setPreferences)

        if self.headless:
            if len(args) < 3:
                print('Not enough arguments. Headless mode requires an input file.')
            elif not startupFileLoaded:
                print('Could not load motor file')
                sys.exit(1)
            else:
                motor = self.fileManager.getCurrentMotor()
                simres = motor.runSimulation()
                for alert in simres.alerts:
                    print(motorlib.alertLevelNames[alert.level] + '(' + motorlib.alertTypeNames[alert.type] + ', ' + alert.location + '): ' + alert.description)
                print()
                if '-o' in args:
                    with open(args[args.index('-o') + 1], 'w') as outputFile:
                        outputFile.write(simres.getCSV(self.preferencesManager.preferences))
                else:
                    print(simres.getCSV(self.preferencesManager.preferences))
            sys.exit(0)

        else:
            self.window = uilib.widgets.mainWindow.Window(self)
            self.preferencesManager.publishPreferences()
            if startupFileLoaded:
                self.fileManager.sendTitleUpdate()
            self.window.show()

    def outputMessage(self, content, title='openMotor'):
        if self.headless:
            print(content)
        else:
            msg = QMessageBox()
            msg.setText(content)
            msg.setWindowTitle(title)
            msg.exec_()

    def outputException(self, exception, text, title='openMotor - Error'):
        if self.headless:
            print(text + " " + str(exception))
        else:
            msg = QMessageBox()
            msg.setText(text)
            msg.setInformativeText(str(exception))
            msg.setWindowTitle(title)
            msg.exec_()
