from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.uic import loadUi
import sys
import yaml

import motorlib
import uilib

class Window(QMainWindow):

    preferencesChanged = pyqtSignal(object)

    def __init__(self, startupFile = None):
        QWidget.__init__(self)
        loadUi("resources/MainWindow.ui", self)

        self.appVersion = '0.0.0'

        self.preferences = uilib.defaultPreferences()
        self.loadPreferences()
        self.preferencesWindow = uilib.PreferencesWindow()
        self.preferencesWindow.preferencesApplied.connect(self.applyPreferences)

        self.propManager = uilib.propellantManager()
        self.propManager.updated.connect(self.propListChanged)
        self.preferencesChanged.connect(self.propManager.setPreferences)

        self.motorStatLabels = [self.labelMotorDesignation, self.labelImpulse, self.labelDeliveredISP, self.labelBurnTime,
                                self.labelAveragePressure, self.labelPeakPressure, self.labelInitialKN, self.labelPeakKN,
                                self.labelPropellantMass, self.labelPropellantLength, self.labelPortThroatRatio, self.labelPeakMassFlux]

        self.fileManager = uilib.fileManager()
        self.fileManager.newFile()
        self.fileManager.fileNameChanged.connect(self.updateWindowTitle)
        if startupFile is not None:
            self.fileManager.load(startupFile)

        self.engExporter = uilib.engExportMenu()
        self.preferencesChanged.connect(self.engExporter.setPreferences)
        self.csvExporter = uilib.csvExportMenu()
        self.preferencesChanged.connect(self.csvExporter.setPreferences)

        self.simulationManager = uilib.simulationManager()
        self.preferencesChanged.connect(self.simulationManager.setPreferences)
        self.simulationManager.newSimulationResult.connect(self.updateMotorStats)
        self.simulationManager.newSimulationResult.connect(self.graphWidget.showData)
        self.simulationManager.newSimulationResult.connect(self.engExporter.acceptSimResult)
        self.simulationManager.newSimulationResult.connect(self.csvExporter.acceptSimResult)

        self.aboutDialog = uilib.aboutDialog(self.appVersion)

        self.toolManager = uilib.toolManager(self.fileManager, self.simulationManager, self.propManager)
        self.preferencesChanged.connect(self.toolManager.setPreferences)
        self.toolManager.setupMenu(self.menuTools)
        self.toolManager.changeApplied.connect(self.updateGrainTable)

        self.preferencesChanged.emit(self.preferences)
        self.setupMotorStats()
        self.setupMotorEditor()
        self.setupGrainAddition()
        self.setupMenu()
        self.setupPropSelector()
        self.setupGrainTable()
        self.setupGraph()

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
        self.motorEditor.setPreferences(self.preferences)
        self.pushButtonEditGrain.pressed.connect(self.editGrain)
        self.motorEditor.changeApplied.connect(self.applyChange)
        self.motorEditor.closed.connect(self.checkGrainSelection) # Enables only buttons for actions possible given the selected grain

    def setupGrainAddition(self):
        self.comboBoxGrainGeometry.addItems(motorlib.grainTypes.keys())
        self.pushButtonAddGrain.pressed.connect(self.addGrain)

    def setupMenu(self):
        #File menu
        self.actionNew.triggered.connect(self.newMotor)
        self.actionSave.triggered.connect(self.fileManager.save)
        self.actionSaveAs.triggered.connect(self.fileManager.saveAs)
        self.actionOpen.triggered.connect(self.loadMotor)
        self.actionENGFile.triggered.connect(self.engExporter.open)
        self.actionCSV.triggered.connect(self.csvExporter.open)
        self.actionQuit.triggered.connect(self.closeEvent)

        #Edit menu
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.actionPreferences.triggered.connect(self.showPreferences)
        self.actionPropellantEditor.triggered.connect(self.propManager.showMenu)

        #Sim
        self.actionRunSimulation.triggered.connect(self.runSimulation)

        #Help
        self.actionAboutOpenMotor.triggered.connect(self.aboutDialog.show)

    def setupPropSelector(self):
        self.pushButtonPropEditor.pressed.connect(self.propManager.showMenu)
        self.populatePropSelector()
        self.comboBoxPropellant.currentIndexChanged.connect(self.propChooserChanged)

    def disablePropSelector(self):
        self.pushButtonPropEditor.pressed.disconnect()
        self.comboBoxPropellant.currentIndexChanged.disconnect()

    def populatePropSelector(self):
        self.comboBoxPropellant.clear()
        self.comboBoxPropellant.addItems(self.propManager.getNames())

    def setupGrainTable(self):
        self.tableWidgetGrainList.clearContents()

        header = self.tableWidgetGrainList.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.updateGrainTable()

        self.pushButtonMoveGrainUp.pressed.connect(lambda: self.moveGrain(-1))
        self.pushButtonMoveGrainDown.pressed.connect(lambda: self.moveGrain(1))
        self.pushButtonDeleteGrain.pressed.connect(self.deleteGrain)

        self.tableWidgetGrainList.itemSelectionChanged.connect(self.checkGrainSelection)
        self.checkGrainSelection()

    def setupGraph(self):
        self.graphWidget.resetPlot()
        self.graphWidget.setPreferences(self.preferences)

    def applyChange(self, propDict):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
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
            print("Motor's propellant must have been deleted, readding")
            self.propManager.propellants.append(cm.propellant)
        self.populatePropSelector()
        self.setupPropSelector()
        self.comboBoxPropellant.setCurrentText(cm.propellant.getProperty("name"))

    def propChooserChanged(self):
        cm = self.fileManager.getCurrentMotor()
        cm.propellant = self.propManager.propellants[self.comboBoxPropellant.currentIndex()]
        self.fileManager.addNewMotorHistory(cm)

    def updateGrainTable(self):
        cm = self.fileManager.getCurrentMotor()
        self.tableWidgetGrainList.setRowCount(len(cm.grains) + 1)
        for gid, grain in enumerate(cm.grains):
            self.tableWidgetGrainList.setItem(gid, 0, QTableWidgetItem(grain.geomName))
            self.tableWidgetGrainList.setItem(gid, 1, QTableWidgetItem(grain.getDetailsString(self.preferences)))

        self.tableWidgetGrainList.setItem(len(cm.grains), 0, QTableWidgetItem('Nozzle'))
        self.tableWidgetGrainList.setItem(len(cm.grains), 1, QTableWidgetItem(cm.nozzle.getDetailsString(self.preferences)))

    def toggleGrainEditButtons(self, state, grainTable = True):
        if grainTable:
            self.tableWidgetGrainList.setEnabled(state)
        self.pushButtonDeleteGrain.setEnabled(state)
        self.pushButtonEditGrain.setEnabled(state)
        self.pushButtonMoveGrainDown.setEnabled(state)
        self.pushButtonMoveGrainUp.setEnabled(state)

    def toggleGrainButtons(self, state):
        self.toggleGrainEditButtons(state)
        self.comboBoxPropellant.setEnabled(state)
        self.comboBoxGrainGeometry.setEnabled(state)
        self.pushButtonAddGrain.setEnabled(state)

    def checkGrainSelection(self):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            self.toggleGrainButtons(True)
            if gid == 0: # Top grain selected
                self.pushButtonMoveGrainUp.setEnabled(False)
            if gid == len(cm.grains) - 1: # Bottom grain selected
                self.pushButtonMoveGrainDown.setEnabled(False)
            elif gid == len(cm.grains):
                self.pushButtonMoveGrainUp.setEnabled(False)
                self.pushButtonMoveGrainDown.setEnabled(False)
                self.pushButtonDeleteGrain.setEnabled(False)
        else:
            self.toggleGrainEditButtons(False, False)

    def moveGrain(self, offset):
        cm = self.fileManager.getCurrentMotor()
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains) and gid + offset < len(cm.grains) and gid + offset >= 0:
                cm.grains[gid + offset], cm.grains[gid] = cm.grains[gid], cm.grains[gid + offset]
                self.tableWidgetGrainList.selectRow(gid + offset)
                self.fileManager.addNewMotorHistory(cm)
                self.updateGrainTable()

    def editGrain(self):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                self.motorEditor.loadGrain(cm.grains[gid])
            else:
                self.motorEditor.loadNozzle(cm.nozzle)
            self.toggleGrainButtons(False)

    def deleteGrain(self):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
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
        newGrain = motorlib.grainTypes[self.comboBoxGrainGeometry.currentText()]()
        cm.grains.append(newGrain)
        self.fileManager.addNewMotorHistory(cm)
        self.updateGrainTable()
        self.tableWidgetGrainList.selectRow(len(cm.grains) - 1)
        self.motorEditor.loadGrain(cm.grains[-1])
        self.checkGrainSelection()
        self.toggleGrainButtons(False)

    def formatMotorStat(self, quantity, inUnit):
        convUnit = self.preferences.getUnit(inUnit)
        return str(round(motorlib.convert(quantity, inUnit, convUnit), 3)) + ' ' + convUnit

    def updateMotorStats(self, simResult):
        self.labelMotorDesignation.setText(simResult.getDesignation())
        self.labelImpulse.setText(self.formatMotorStat(simResult.getImpulse(), 'Ns'))
        self.labelDeliveredISP.setText(self.formatMotorStat(simResult.getISP(), 's'))
        self.labelBurnTime.setText(self.formatMotorStat(simResult.getBurnTime(), 's'))

        self.labelAveragePressure.setText(self.formatMotorStat(simResult.getAveragePressure(), 'Pa'))
        self.labelPeakPressure.setText(self.formatMotorStat(simResult.getMaxPressure(), 'Pa'))
        self.labelInitialKN.setText(self.formatMotorStat(simResult.getInitialKN(), ''))
        self.labelPeakKN.setText(self.formatMotorStat(simResult.getPeakKN(), ''))

        self.labelPropellantMass.setText(self.formatMotorStat(simResult.getPropellantMass(), 'kg'))
        self.labelPropellantLength.setText(self.formatMotorStat(simResult.getPropellantLength(), 'm'))

        if simResult.getPortRatio() is not None:
            self.labelPortThroatRatio.setText(self.formatMotorStat(simResult.getPortRatio(), ''))
            self.labelPeakMassFlux.setText(self.formatMotorStat(simResult.getPeakMassFlux(), 'kg/(m^2*s)'))

        else:
            self.labelPortThroatRatio.setText('-')
            self.labelPeakMassFlux.setText('-')

    def runSimulation(self):
        self.resetOutput()
        cm = self.fileManager.getCurrentMotor()
        self.simulationManager.runSimulation(cm)

    def resetOutput(self):
        self.setupMotorStats()
        self.graphWidget.resetPlot()
        self.updateGrainTable()

    def undo(self):
        self.fileManager.undo()
        self.updateGrainTable()
        self.checkGrainSelection()
        cm = self.fileManager.getCurrentMotor()
        self.comboBoxPropellant.setCurrentText(cm.propellant.getProperty("name"))

    def redo(self):
        self.fileManager.redo()
        self.updateGrainTable()
        self.checkGrainSelection()
        cm = self.fileManager.getCurrentMotor()
        self.comboBoxPropellant.setCurrentText(cm.propellant.getProperty("name"))

    def newMotor(self):
        self.fileManager.newFile()
        self.resetOutput()

    def loadMotor(self):
        self.disablePropSelector()
        if self.fileManager.load():
            self.resetOutput()
            self.updateGrainTable()

            cm = self.fileManager.getCurrentMotor()
            if cm.propellant.getProperty('name') not in self.propManager.getNames():
                print("Propellant not in library, adding")
                self.propManager.propellants.append(cm.propellant)
                self.propManager.savePropellants()
            else:
                if cm.propellant.getProperties() != self.propManager.getPropellantByName(cm.propellant.getProperty('name')).getProperties():
                    print("Loaded propellant name matches existing propellant, but properties differ. Using propellant from library.")
                    cm.propellant = self.propManager.getPropellantByName(cm.propellant.getProperty('name'))
                    self.fileManager.addNewMotorHistory(cm)

            self.setupPropSelector()
            self.comboBoxPropellant.setCurrentText(cm.propellant.getProperty("name"))

    def closeEvent(self, event = None):
        if self.fileManager.unsavedCheck():
            sys.exit()
        else:
            if event is not None:
                if type(event) is not bool:
                    event.ignore()

    def loadPreferences(self):
        try:
            with open('preferences.yaml', 'r') as prefFile:
                prefDict = yaml.load(prefFile)
                self.preferences.applyDict(prefDict)
        except FileNotFoundError:
            self.savePreferences()

    def savePreferences(self):
        try:
            with open('preferences.yaml', 'w') as prefFile:
                yaml.dump(self.preferences.getDict(), prefFile)
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
            with open(sys.argv[-1], 'r') as motorFile, open('preferences.yaml', 'r') as prefFile:
                prefDict = yaml.load(prefFile)
                preferences = uilib.preferences()
                preferences.applyDict(prefDict)
                motorData = yaml.load(motorFile)
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
    else:
        app = QApplication(sys.argv)
        startupFile = None
        if len(sys.argv) > 1:
            startupFile = sys.argv[-1]
        w = Window(startupFile)
        sys.exit(app.exec_())
