import sys
import matplotlib.pyplot as plt
import matplotlib as mpl

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

import motorlib
from motorlib import simResult
from uilib import preferencesManager, propellantManager, simulationManager, fileManager, toolManager
from uilib import importExportManager
import uilib.widgets.mainWindow
from uilib.logger import logger

class App(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.icon = QIcon('resources/oMIconCyclesSmall.png')

        self.headless = '-h' in args

        if not self.headless and self.isDarkMode():
            # Change these settings before any graph widgets are built, so they apply everywhere
            plt.style.use('dark_background')
            mpl.rcParams['axes.facecolor'] = '1e1e1e'
            mpl.rcParams['figure.facecolor'] = '1e1e1e'

        self.preferencesManager = uilib.preferencesManager.PreferencesManager()

        self.propellantManager = uilib.propellantManager.PropellantManager()
        self.preferencesManager.preferencesChanged.connect(self.propellantManager.setPreferences)

        self.simulationManager = uilib.simulationManager.SimulationManager()
        self.preferencesManager.preferencesChanged.connect(self.simulationManager.setPreferences)

        self.fileManager = uilib.fileManager.FileManager(self)
        startupFileLoaded = False
        if len(args) > 1 and args[-1][0] != '-':
            startupFileLoaded = self.fileManager.load(args[-1])
        self.propellantManager.updated.connect(self.fileManager.updatePropellant)

        self.toolManager = uilib.toolManager.ToolManager(self)
        self.preferencesManager.preferencesChanged.connect(self.toolManager.setPreferences)

        self.importExportManager = uilib.importExportManager.ImportExportManager(self)
        self.preferencesManager.preferencesChanged.connect(self.importExportManager.setPreferences)
        self.simulationManager.newSimulationResult.connect(self.importExportManager.acceptSimRes)
        self.fileManager.newMotor.connect(self.importExportManager.acceptNewMotor)

        if self.headless:
            if len(args) < 3:
                print('Not enough arguments. Headless mode requires an input file.')
            elif not startupFileLoaded:
                print('Could not load motor file')
                sys.exit(1)
            else:
                motor = self.fileManager.getCurrentMotor()
                simulationResult = motor.runSimulation()
                for alert in simulationResult.alerts:
                    print('{} ({}, {}): {}'.format(motorlib.simResult.alertLevelNames[alert.level],
                        motorlib.simResult.alertTypeNames[alert.type],
                        alert.location,
                        alert.description))
                print()
                if '-o' in args:
                    with open(args[args.index('-o') + 1], 'w') as outputFile:
                        outputFile.write(simulationResult.getCSV(self.preferencesManager.preferences))
                else:
                    print(simulationResult.getCSV(self.preferencesManager.preferences))
            sys.exit(0)

        else:
            logger.log('Opening window (dark mode: {})'.format(self.isDarkMode()))
            self.window = uilib.widgets.mainWindow.Window(self)
            self.preferencesManager.publishPreferences()
            if startupFileLoaded:
                self.fileManager.sendTitleUpdate()
            self.window.show()
            logger.log('Window opened')

    def isDarkMode(self):
        if self.headless:
            return False

        return self.styleHints().colorScheme() == Qt.ColorScheme.Dark

    def outputMessage(self, content, title='openMotor'):
        if self.headless:
            print(content)
        else:
            logger.log(content)
            msg = QMessageBox()
            msg.setWindowIcon(self.icon)
            msg.setText(content)
            msg.setWindowTitle(title)
            msg.exec()

    def outputException(self, exception, text, title='openMotor - Error'):
        if self.headless:
            print(text + " " + str(exception))
        else:
            logger.error(text)
            logger.error(exception)
            msg = QMessageBox()
            msg.setWindowIcon(self.icon)
            msg.setText(text)
            msg.setInformativeText(str(exception))
            msg.setWindowTitle(title)
            msg.exec()
