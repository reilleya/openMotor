from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QMessageBox, QTableWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import sys
import yaml

import motorlib
import uilib

from uilib.views.MainWindow_ui import Ui_MainWindow


class Window(QMainWindow):

    preferencesChanged = pyqtSignal(object)

    def __init__(self, startupFile = None):
        QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.appVersion = uilib.fileIO.appVersion
        self.appVersionStr = uilib.fileIO.appVersionStr

        self.preferences = uilib.defaultPreferences()
        self.loadPreferences()
        self.preferencesWindow = uilib.PreferencesWindow()
        self.preferencesWindow.preferencesApplied.connect(self.applyPreferences)

        self.propManager = uilib.propellantManager()
        self.propManager.updated.connect(self.propListChanged)
        self.preferencesChanged.connect(self.propManager.setPreferences)

        self.motorStatLabels = [self.ui.labelMotorDesignation, self.ui.labelImpulse, self.ui.labelDeliveredISP, self.ui.labelBurnTime,
                                self.ui.labelAveragePressure, self.ui.labelPeakPressure, self.ui.labelInitialKN, self.ui.labelPeakKN,
                                self.ui.labelPropellantMass, self.ui.labelPropellantLength, self.ui.labelPortThroatRatio, self.ui.labelPeakMassFlux]

        self.fileManager = uilib.fileManager()
        self.fileManager.fileNameChanged.connect(self.updateWindowTitle)

        self.engExporter = uilib.engExportMenu()
        self.preferencesChanged.connect(self.engExporter.setPreferences)
        self.csvExporter = uilib.csvExportMenu()
        self.preferencesChanged.connect(self.csvExporter.setPreferences)

        self.simulationManager = uilib.simulationManager()
        self.preferencesChanged.connect(self.simulationManager.setPreferences)
        self.simulationManager.newSimulationResult.connect(self.updateMotorStats)
        self.simulationManager.newSimulationResult.connect(self.ui.graphWidget.showData)
        self.simulationManager.newSimulationResult.connect(self.engExporter.acceptSimResult)
        self.simulationManager.newSimulationResult.connect(self.csvExporter.acceptSimResult)

        self.aboutDialog = uilib.aboutDialog(self.appVersionStr)

        self.toolManager = uilib.toolManager(self.fileManager, self.simulationManager, self.propManager)
        self.preferencesChanged.connect(self.toolManager.setPreferences)
        self.toolManager.setupMenu(self.ui.menuTools)
        self.toolManager.changeApplied.connect(self.updateGrainTable)

        self.burnsimManager = uilib.burnsimManager(self.fileManager)

        self.preferencesChanged.emit(self.preferences)
        self.setupMotorStats()
        self.setupMotorEditor()
        self.setupGrainAddition()
        self.setupMenu()
        self.setupPropSelector()
        self.setupGrainTable()
        self.setupGraph()

        self.updatePropBoxSelection() # This will go away when we remove the startup motor

        if startupFile is not None:
            self.loadMotor(startupFile)

        self.show()

    def updateWindowTitle(self, name, saved):
        unsavedStr = '*' if not saved else ''
        if name is not None:
            self.setWindowTitle('openMotor - ' + name + unsavedStr)
        else:
            self.setWindowTitle('openMotor - ' + unsavedStr)

    def setupMotorStats(self):
        for label in self.motorStatLabels:
            label.setText("-")

    def setupMotorEditor(self):
        self.ui.motorEditor.setPreferences(self.preferences)
        self.ui.pushButtonEditGrain.pressed.connect(self.editGrain)
        self.ui.motorEditor.changeApplied.connect(self.applyChange)
        self.ui.motorEditor.closed.connect(self.checkGrainSelection) # Enables only buttons for actions possible given the selected grain

    def setupGrainAddition(self):
        self.ui.comboBoxGrainGeometry.addItems(motorlib.grainTypes.keys())
        self.ui.pushButtonAddGrain.pressed.connect(self.addGrain)

    def setupMenu(self):
        # File menu
        self.ui.actionNew.triggered.connect(self.newMotor)
        self.ui.actionSave.triggered.connect(self.fileManager.save)
        self.ui.actionSaveAs.triggered.connect(self.fileManager.saveAs)
        self.ui.actionOpen.triggered.connect(lambda x: self.loadMotor(None)) # Lambda because the signal passes in an argument
        # Import
        self.ui.actionImportBurnSim.triggered.connect(self.burnSimImport)
        # Export 
        self.ui.actionENGFile.triggered.connect(self.engExporter.open)
        self.ui.actionCSV.triggered.connect(self.csvExporter.open)
        self.ui.actionExportBurnSim.triggered.connect(self.burnsimManager.showExportMenu)

        self.ui.actionQuit.triggered.connect(self.closeEvent)

        # Edit menu
        self.ui.actionUndo.triggered.connect(self.undo)
        self.ui.actionRedo.triggered.connect(self.redo)
        self.ui.actionPreferences.triggered.connect(self.showPreferences)
        self.ui.actionPropellantEditor.triggered.connect(self.propManager.showMenu)

        # Sim
        self.ui.actionRunSimulation.triggered.connect(self.runSimulation)

        # Help
        self.ui.actionAboutOpenMotor.triggered.connect(self.aboutDialog.show)

    def setupPropSelector(self):
        self.ui.pushButtonPropEditor.pressed.connect(self.propManager.showMenu)
        self.populatePropSelector()
        self.ui.comboBoxPropellant.currentIndexChanged.connect(self.propChooserChanged)

    def populatePropSelector(self):
        self.ui.comboBoxPropellant.clear()
        self.ui.comboBoxPropellant.addItems(self.propManager.getNames())

    def disablePropSelector(self):
        self.ui.comboBoxPropellant.blockSignals(True)

    def enablePropSelector(self):
        self.ui.comboBoxPropellant.blockSignals(False)

    def updatePropBoxSelection(self):
        self.disablePropSelector()
        cm = self.fileManager.getCurrentMotor()
        self.ui.comboBoxPropellant.setCurrentText(self.fileManager.getCurrentMotor().propellant.getProperty("name"))
        self.enablePropSelector()

    def setupGrainTable(self):
        self.ui.tableWidgetGrainList.clearContents()
        self.ui.tableWidgetGrainList.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.ui.tableWidgetGrainList.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.updateGrainTable()

        self.ui.pushButtonMoveGrainUp.pressed.connect(lambda: self.moveGrain(-1))
        self.ui.pushButtonMoveGrainDown.pressed.connect(lambda: self.moveGrain(1))
        self.ui.pushButtonDeleteGrain.pressed.connect(self.deleteGrain)
        self.ui.pushButtonCopyGrain.pressed.connect(self.copyGrain)

        self.ui.tableWidgetGrainList.itemSelectionChanged.connect(self.checkGrainSelection)
        self.checkGrainSelection()

    def setupGraph(self):
        self.ui.graphWidget.resetPlot()
        self.ui.graphWidget.setPreferences(self.preferences)

    def applyChange(self, propDict):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                cm.grains[gid].setProperties(propDict)
            else:
                cm.nozzle.setProperties(propDict)
        self.fileManager.addNewMotorHistory(cm)
        self.updateGrainTable()

    def propListChanged(self):
        self.resetOutput()
        self.disablePropSelector()
        cm = self.fileManager.getCurrentMotor()
        if cm.propellant.getProperty("name") not in self.propManager.getNames():
            self.showMessage("The current motor's propellant has been removed from the library. It has been added back.")
            self.propManager.propellants.append(cm.propellant)
            self.propManager.savePropellants()
        self.populatePropSelector()
        self.updatePropBoxSelection()
        self.enablePropSelector()

    def propChooserChanged(self):
        cm = self.fileManager.getCurrentMotor()
        cm.propellant = self.propManager.propellants[self.ui.comboBoxPropellant.currentIndex()]
        self.fileManager.addNewMotorHistory(cm)

    def updateGrainTable(self):
        cm = self.fileManager.getCurrentMotor()
        self.ui.tableWidgetGrainList.setRowCount(len(cm.grains) + 1)
        for gid, grain in enumerate(cm.grains):
            self.ui.tableWidgetGrainList.setItem(gid, 0, QTableWidgetItem(grain.geomName))
            self.ui.tableWidgetGrainList.setItem(gid, 1, QTableWidgetItem(grain.getDetailsString(self.preferences)))

        self.ui.tableWidgetGrainList.setItem(len(cm.grains), 0, QTableWidgetItem('Nozzle'))
        self.ui.tableWidgetGrainList.setItem(len(cm.grains), 1, QTableWidgetItem(cm.nozzle.getDetailsString(self.preferences)))

    def toggleGrainEditButtons(self, state, grainTable = True):
        if grainTable:
            self.ui.tableWidgetGrainList.setEnabled(state)
        self.ui.pushButtonDeleteGrain.setEnabled(state)
        self.ui.pushButtonEditGrain.setEnabled(state)
        self.ui.pushButtonCopyGrain.setEnabled(state)
        self.ui.pushButtonMoveGrainDown.setEnabled(state)
        self.ui.pushButtonMoveGrainUp.setEnabled(state)

    def toggleGrainButtons(self, state):
        self.toggleGrainEditButtons(state)
        self.ui.comboBoxPropellant.setEnabled(state)
        self.ui.comboBoxGrainGeometry.setEnabled(state)
        self.ui.pushButtonAddGrain.setEnabled(state)

    def checkGrainSelection(self):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            self.toggleGrainButtons(True)
            if gid == 0: # Top grain selected
                self.ui.pushButtonMoveGrainUp.setEnabled(False)
            if gid == len(cm.grains) - 1: # Bottom grain selected
                self.ui.pushButtonMoveGrainDown.setEnabled(False)
            elif gid == len(cm.grains): # Nozzle selected
                self.ui.pushButtonMoveGrainUp.setEnabled(False)
                self.ui.pushButtonMoveGrainDown.setEnabled(False)
                self.ui.pushButtonDeleteGrain.setEnabled(False)
                self.ui.pushButtonCopyGrain.setEnabled(False)
        else:
            self.toggleGrainEditButtons(False, False)

    def moveGrain(self, offset):
        cm = self.fileManager.getCurrentMotor()
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains) and gid + offset < len(cm.grains) and gid + offset >= 0:
                cm.grains[gid + offset], cm.grains[gid] = cm.grains[gid], cm.grains[gid + offset]
                self.ui.tableWidgetGrainList.selectRow(gid + offset)
                self.fileManager.addNewMotorHistory(cm)
                self.updateGrainTable()

    def editGrain(self):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                self.ui.motorEditor.loadGrain(cm.grains[gid])
            else:
                self.ui.motorEditor.loadNozzle(cm.nozzle)
            self.toggleGrainButtons(False)

    def copyGrain(self):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                cm.grains.append(cm.grains[gid])
                self.fileManager.addNewMotorHistory(cm)
                self.updateGrainTable()
                self.checkGrainSelection()

    def deleteGrain(self):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                del cm.grains[gid]
                self.fileManager.addNewMotorHistory(cm)
                self.updateGrainTable()
                self.checkGrainSelection()

    def addGrain(self):
        cm = self.fileManager.getCurrentMotor()
        newGrain = motorlib.grainTypes[self.ui.comboBoxGrainGeometry.currentText()]()
        if len(cm.grains) != 0:
            newGrain.setProperty('diameter', cm.grains[-1].getProperty('diameter'))
        cm.grains.append(newGrain)
        self.fileManager.addNewMotorHistory(cm)
        self.updateGrainTable()
        self.ui.tableWidgetGrainList.selectRow(len(cm.grains) - 1)
        self.ui.motorEditor.loadGrain(cm.grains[-1])
        self.checkGrainSelection()
        self.toggleGrainButtons(False)

    def formatMotorStat(self, quantity, inUnit):
        convUnit = self.preferences.getUnit(inUnit)
        return str(round(motorlib.convert(quantity, inUnit, convUnit), 3)) + ' ' + convUnit

    def updateMotorStats(self, simResult):
        self.ui.labelMotorDesignation.setText(simResult.getDesignation())
        self.ui.labelImpulse.setText(self.formatMotorStat(simResult.getImpulse(), 'Ns'))
        self.ui.labelDeliveredISP.setText(self.formatMotorStat(simResult.getISP(), 's'))
        self.ui.labelBurnTime.setText(self.formatMotorStat(simResult.getBurnTime(), 's'))

        self.ui.labelAveragePressure.setText(self.formatMotorStat(simResult.getAveragePressure(), 'Pa'))
        self.ui.labelPeakPressure.setText(self.formatMotorStat(simResult.getMaxPressure(), 'Pa'))
        self.ui.labelInitialKN.setText(self.formatMotorStat(simResult.getInitialKN(), ''))
        self.ui.labelPeakKN.setText(self.formatMotorStat(simResult.getPeakKN(), ''))

        self.ui.labelPropellantMass.setText(self.formatMotorStat(simResult.getPropellantMass(), 'kg'))
        self.ui.labelPropellantLength.setText(self.formatMotorStat(simResult.getPropellantLength(), 'm'))

        if simResult.getPortRatio() is not None:
            self.ui.labelPortThroatRatio.setText(self.formatMotorStat(simResult.getPortRatio(), ''))
            self.ui.labelPeakMassFlux.setText(self.formatMotorStat(simResult.getPeakMassFlux(), 'kg/(m^2*s)') + ' (G: ' + str(simResult.getPeakMassFluxLocation() + 1) + ')')

        else:
            self.ui.labelPortThroatRatio.setText('-')
            self.ui.labelPeakMassFlux.setText('-')

    def runSimulation(self):
        self.resetOutput()
        cm = self.fileManager.getCurrentMotor()
        self.simulationManager.runSimulation(cm)

    def resetOutput(self):
        self.setupMotorStats()
        self.ui.graphWidget.resetPlot()
        self.updateGrainTable()

    def undo(self):
        self.fileManager.undo()
        self.updateGrainTable()
        self.checkGrainSelection()
        self.updatePropBoxSelection()

    def redo(self):
        self.fileManager.redo()
        self.updateGrainTable()
        self.checkGrainSelection()
        self.updatePropBoxSelection()

    def newMotor(self):
        self.fileManager.newFile()
        self.updatePropBoxSelection()
        self.resetOutput()

    def burnSimImport(self):
        self.disablePropSelector()
        if self.burnsimManager.showImportMenu():
            self.postLoadUpdate()
        self.enablePropSelector()

    def loadMotor(self, path = None):
        self.disablePropSelector()
        if self.fileManager.load(path):
            self.postLoadUpdate()
        self.enablePropSelector()

    # Handle the current motor's propellant not being the library
    def postLoadUpdate(self):
        self.resetOutput()
        self.updateGrainTable()

        cm = self.fileManager.getCurrentMotor()
        if cm.propellant.getProperty('name') not in self.propManager.getNames():
            self.showMessage('The propellant from the loaded motor was not in the library, so it was added as "' + cm.propellant.getProperty('name') + '"',
                    'New propellant added')
            self.propManager.propellants.append(cm.propellant)
            self.propManager.savePropellants()
        else:
            if cm.propellant.getProperties() != self.propManager.getPropellantByName(cm.propellant.getProperty('name')).getProperties():
                addedNumber = 1
                while cm.propellant.getProperty('name') + ' (' + str(addedNumber) + ')' in self.propManager.getNames():
                    addedNumber += 1
                cm.propellant.setProperty('name', cm.propellant.getProperty('name') + ' (' + str(addedNumber) + ')')
                self.propManager.propellants.append(cm.propellant)
                self.propManager.savePropellants()
                self.fileManager.overrideCurrentMotor(cm) # To change the propellant name while disallowing an undo to the wrong name
                self.showMessage('The propellant from the loaded motor matches an existing item in the library, but they have different properties. The propellant from the motor has been added to the library as "' + cm.propellant.getProperty('name') + '"',
                    'New propellant added')

        self.populatePropSelector()
        self.updatePropBoxSelection()

    def showMessage(self, message, title = 'openMotor'):
        msg = QMessageBox()
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def closeEvent(self, event = None):
        if self.fileManager.unsavedCheck():
            sys.exit()
        else:
            if event is not None:
                if type(event) is not bool:
                    event.ignore()

    def loadPreferences(self):
        try:
            prefDict = uilib.loadFile(uilib.fileIO.getConfigPath() + 'preferences.yaml', uilib.fileTypes.PREFERENCES)
            self.preferences.applyDict(prefDict)
        except FileNotFoundError:
            self.savePreferences()

    def savePreferences(self):
        try:
            uilib.saveFile(uilib.fileIO.getConfigPath() + 'preferences.yaml', self.preferences.getDict(), uilib.fileTypes.PREFERENCES)
        except:
            print('Unable to save preferences')

    def applyPreferences(self, prefDict):
        self.preferences.applyDict(prefDict)
        self.savePreferences()
        self.updateGrainTable()
        self.setupMotorStats()
        self.setupGraph()
        self.preferencesChanged.emit(self.preferences)

    def showPreferences(self):
        self.preferencesWindow.load(self.preferences)
        self.preferencesWindow.show()


if __name__ == '__main__':
    if '-h' in sys.argv:
        if len(sys.argv) < 3:
            print('Not enough arguments. Headless mode requires an input file.')
        else:
            preferences = uilib.defaultPreferences()
            try:
                prefDict = uilib.loadFile('preferences.yaml', uilib.fileTypes.PREFERENCES)
                preferences.applyDict(prefDict)
            except:
                print('Preferences could not be loaded, using default')

            try:
                motorData = uilib.loadFile(sys.argv[-1], uilib.fileTypes.MOTOR)
                motor = motorlib.motor()
                motor.loadDict(motorData)
                simres = motor.runSimulation(preferences)
                for alert in simres.alerts:
                    print(motorlib.alertLevelNames[alert.level] + '(' + motorlib.alertTypeNames[alert.type] + ', ' + alert.location + '): ' + alert.description)
                print()
                if '-o' in sys.argv:
                    with open(sys.argv[sys.argv.index('-o') + 1], 'w') as outputFile:
                        outputFile.write(simres.getCSV(preferences))
                else:
                    print(simres.getCSV(preferences))
            except:
                print('Motor could not be loaded')

    else:
        app = QApplication(sys.argv)
        startupFile = None
        if len(sys.argv) > 1:
            startupFile = sys.argv[-1]
        w = Window(startupFile)
        sys.exit(app.exec_())
