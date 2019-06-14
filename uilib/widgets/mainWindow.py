import sys

from PyQt5.QtWidgets import QWidget, QMainWindow, QTableWidgetItem, QHeaderView, QMessageBox, QTableWidget

import motorlib
from uilib import burnsimManager
from uilib import engExport, csvExport, imageExport
import uilib.widgets.aboutDialog
import uilib.widgets.preferencesMenu
from uilib.views.MainWindow_ui import Ui_MainWindow

class Window(QMainWindow):
    def __init__(self, app):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.app = app

        self.appVersion = uilib.fileIO.appVersion
        self.appVersionStr = uilib.fileIO.appVersionStr

        self.app.preferencesManager.preferencesChanged.connect(self.applyPreferences)

        self.app.propellantManager.updated.connect(self.propListChanged)

        self.motorStatLabels = [self.ui.labelMotorDesignation, self.ui.labelImpulse, self.ui.labelDeliveredISP, self.ui.labelBurnTime,
                                self.ui.labelAveragePressure, self.ui.labelPeakPressure, self.ui.labelInitialKN, self.ui.labelPeakKN,
                                self.ui.labelPropellantMass, self.ui.labelPropellantLength, self.ui.labelPortThroatRatio, self.ui.labelPeakMassFlux]

        self.app.fileManager.fileNameChanged.connect(self.updateWindowTitle)

        self.engExporter = uilib.engExport.ENGExportMenu()
        self.app.preferencesManager.preferencesChanged.connect(self.engExporter.setPreferences)
        self.csvExporter = uilib.csvExport.CSVExportMenu()
        self.app.preferencesManager.preferencesChanged.connect(self.csvExporter.setPreferences)
        self.imageExporter = uilib.imageExport.ImageExportMenu()
        self.app.preferencesManager.preferencesChanged.connect(self.imageExporter.setPreferences)

        self.app.simulationManager.newSimulationResult.connect(self.updateMotorStats)
        self.app.simulationManager.newSimulationResult.connect(self.ui.graphWidget.showData)
        self.app.simulationManager.newSimulationResult.connect(self.engExporter.acceptSimResult)
        self.app.simulationManager.newSimulationResult.connect(self.csvExporter.acceptSimResult)
        self.app.simulationManager.newSimulationResult.connect(self.imageExporter.acceptSimResult)

        self.aboutDialog = uilib.widgets.aboutDialog.AboutDialog(self.appVersionStr)

        self.app.toolManager.setupMenu(self.ui.menuTools)
        self.app.toolManager.changeApplied.connect(self.postLoadUpdate)

        self.burnsimManager = uilib.burnsimManager.BurnsimManager(self.app.fileManager)

        self.setupMotorStats()
        self.setupMotorEditor()
        self.setupGrainAddition()
        self.setupMenu()
        self.setupPropSelector()
        self.setupGrainTable()
        self.setupGraph()

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
        self.ui.motorEditor.setPreferences(self.app.preferencesManager.preferences)
        self.ui.pushButtonEditGrain.pressed.connect(self.editGrain)
        self.ui.motorEditor.changeApplied.connect(self.applyChange)
        self.ui.motorEditor.closed.connect(self.checkGrainSelection) # Enables only buttons for actions possible given the selected grain

    def setupGrainAddition(self):
        self.ui.comboBoxGrainGeometry.addItems(motorlib.grains.grainTypes.keys())
        self.ui.pushButtonAddGrain.pressed.connect(self.addGrain)

    def setupMenu(self):
        # File menu
        self.ui.actionNew.triggered.connect(self.newMotor)
        self.ui.actionSave.triggered.connect(self.app.fileManager.save)
        self.ui.actionSaveAs.triggered.connect(self.app.fileManager.saveAs)
        self.ui.actionOpen.triggered.connect(lambda x: self.loadMotor(None)) # Lambda because the signal passes in an argument
        # Import
        self.ui.actionImportBurnSim.triggered.connect(self.burnSimImport)
        # Export
        self.ui.actionENGFile.triggered.connect(self.engExporter.open)
        self.ui.actionImage.triggered.connect(self.imageExporter.open)
        self.ui.actionCSV.triggered.connect(self.csvExporter.open)
        self.ui.actionExportBurnSim.triggered.connect(self.burnsimManager.showExportMenu)

        self.ui.actionQuit.triggered.connect(self.closeEvent)

        # Edit menu
        self.ui.actionUndo.triggered.connect(self.undo)
        self.ui.actionRedo.triggered.connect(self.redo)
        self.ui.actionPreferences.triggered.connect(self.app.preferencesManager.showMenu)
        self.ui.actionPropellantEditor.triggered.connect(self.app.propellantManager.showMenu)

        # Sim
        self.ui.actionRunSimulation.triggered.connect(self.runSimulation)

        # Help
        self.ui.actionAboutOpenMotor.triggered.connect(self.aboutDialog.show)

    def setupPropSelector(self):
        self.ui.pushButtonPropEditor.pressed.connect(self.app.propellantManager.showMenu)
        self.populatePropSelector()
        self.ui.comboBoxPropellant.currentIndexChanged.connect(self.propChooserChanged)

    def populatePropSelector(self):
        self.ui.comboBoxPropellant.clear()
        self.ui.comboBoxPropellant.addItem('-')
        self.ui.comboBoxPropellant.addItems(self.app.propellantManager.getNames())

    def disablePropSelector(self):
        self.ui.comboBoxPropellant.blockSignals(True)

    def enablePropSelector(self):
        self.ui.comboBoxPropellant.blockSignals(False)

    def updatePropBoxSelection(self):
        self.disablePropSelector()
        cm = self.app.fileManager.getCurrentMotor()
        prop = self.app.fileManager.getCurrentMotor().propellant
        if prop is None:
            self.ui.comboBoxPropellant.setCurrentText('-')
        else:
            self.ui.comboBoxPropellant.setCurrentText(prop.getProperty("name"))
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
        self.ui.graphWidget.setPreferences(self.app.preferencesManager.preferences)

    def applyChange(self, propDict):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.app.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                cm.grains[gid].setProperties(propDict)
            elif gid == len(cm.grains):
                cm.nozzle.setProperties(propDict)
            else:
                cm.config.setProperties(propDict)
        self.app.fileManager.addNewMotorHistory(cm)
        self.updateGrainTable()

    def propListChanged(self):
        self.resetOutput()
        self.disablePropSelector()
        cm = self.app.fileManager.getCurrentMotor()
        if cm.propellant is not None and cm.propellant.getProperty("name") not in self.app.propellantManager.getNames():
            reply = QMessageBox.question(self, "Propellant deleted",
                                         "The current motor's propellant has been removed from the library. Would you like to add it back?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.app.propellantManager.propellants.append(cm.propellant)
                self.app.propellantManager.savePropellants()
            else:
                cm.propellant = None
                self.app.fileManager.addNewMotorHistory(cm)
        self.populatePropSelector()
        self.updatePropBoxSelection()
        self.enablePropSelector()

    def propChooserChanged(self):
        cm = self.app.fileManager.getCurrentMotor()
        if self.ui.comboBoxPropellant.currentIndex() == 0:
            cm.propellant = None
        else:
            cm.propellant = self.app.propellantManager.propellants[self.ui.comboBoxPropellant.currentIndex() - 1]
        self.app.fileManager.addNewMotorHistory(cm)

    def updateGrainTable(self):
        cm = self.app.fileManager.getCurrentMotor()
        self.ui.tableWidgetGrainList.setRowCount(len(cm.grains) + 2)
        for gid, grain in enumerate(cm.grains):
            self.ui.tableWidgetGrainList.setItem(gid, 0, QTableWidgetItem(grain.geomName))
            self.ui.tableWidgetGrainList.setItem(gid, 1, QTableWidgetItem(grain.getDetailsString(self.app.preferencesManager.preferences)))

        self.ui.tableWidgetGrainList.setItem(len(cm.grains), 0, QTableWidgetItem('Nozzle'))
        self.ui.tableWidgetGrainList.setItem(len(cm.grains), 1, QTableWidgetItem(cm.nozzle.getDetailsString(self.app.preferencesManager.preferences)))

        self.ui.tableWidgetGrainList.setItem(len(cm.grains) + 1, 0, QTableWidgetItem('Config'))
        self.ui.tableWidgetGrainList.setItem(len(cm.grains) + 1, 1, QTableWidgetItem('-'))

        self.repaint() # OSX needs this

    def toggleGrainEditButtons(self, state, grainTable=True):
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
        cm = self.app.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            self.toggleGrainButtons(True)
            if gid == 0: # Top grain selected
                self.ui.pushButtonMoveGrainUp.setEnabled(False)
            if gid == len(cm.grains) - 1: # Bottom grain selected
                self.ui.pushButtonMoveGrainDown.setEnabled(False)
            if gid >= len(cm.grains): # Nozzle or config selected
                self.ui.pushButtonMoveGrainUp.setEnabled(False)
                self.ui.pushButtonMoveGrainDown.setEnabled(False)
                self.ui.pushButtonDeleteGrain.setEnabled(False)
                self.ui.pushButtonCopyGrain.setEnabled(False)
        else:
            self.toggleGrainEditButtons(False, False)
        self.repaint() # OSX needs this

    def moveGrain(self, offset):
        cm = self.app.fileManager.getCurrentMotor()
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains) and gid + offset < len(cm.grains) and gid + offset >= 0:
                cm.grains[gid + offset], cm.grains[gid] = cm.grains[gid], cm.grains[gid + offset]
                self.ui.tableWidgetGrainList.selectRow(gid + offset)
                self.app.fileManager.addNewMotorHistory(cm)
                self.updateGrainTable()

    def editGrain(self):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.app.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                self.ui.motorEditor.loadGrain(cm.grains[gid])
            elif gid == len(cm.grains):
                self.ui.motorEditor.loadNozzle(cm.nozzle)
            else:
                self.ui.motorEditor.loadConfig(cm.config)
            self.toggleGrainButtons(False)

    def copyGrain(self):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.app.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                cm.grains.append(cm.grains[gid])
                self.app.fileManager.addNewMotorHistory(cm)
                self.updateGrainTable()
                self.checkGrainSelection()

    def deleteGrain(self):
        ind = self.ui.tableWidgetGrainList.selectionModel().selectedRows()
        cm = self.app.fileManager.getCurrentMotor()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(cm.grains):
                del cm.grains[gid]
                self.app.fileManager.addNewMotorHistory(cm)
                self.updateGrainTable()
                self.checkGrainSelection()

    def addGrain(self):
        cm = self.app.fileManager.getCurrentMotor()
        newGrain = motorlib.grains.grainTypes[self.ui.comboBoxGrainGeometry.currentText()]()
        if len(cm.grains) != 0:
            newGrain.setProperty('diameter', cm.grains[-1].getProperty('diameter'))
        cm.grains.append(newGrain)
        self.app.fileManager.addNewMotorHistory(cm)
        self.updateGrainTable()
        self.ui.tableWidgetGrainList.selectRow(len(cm.grains) - 1)
        self.ui.motorEditor.loadGrain(cm.grains[-1])
        self.checkGrainSelection()
        self.toggleGrainButtons(False)

    def formatMotorStat(self, quantity, inUnit):
        convUnit = self.app.preferencesManager.preferences.getUnit(inUnit)
        return str(round(motorlib.units.convert(quantity, inUnit, convUnit), 3)) + ' ' + convUnit

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
        cm = self.app.fileManager.getCurrentMotor()
        self.app.simulationManager.runSimulation(cm)

    def resetOutput(self):
        self.setupMotorStats()
        self.ui.graphWidget.resetPlot()
        self.updateGrainTable()

    def undo(self):
        self.app.fileManager.undo()
        self.updateGrainTable()
        self.checkGrainSelection()
        self.updatePropBoxSelection()

    def redo(self):
        self.app.fileManager.redo()
        self.updateGrainTable()
        self.checkGrainSelection()
        self.updatePropBoxSelection()

    def newMotor(self):
        self.app.fileManager.newFile()
        self.updatePropBoxSelection()
        self.resetOutput()

    def burnSimImport(self):
        self.disablePropSelector()
        if self.burnsimManager.showImportMenu():
            self.postLoadUpdate()
        self.enablePropSelector()

    def loadMotor(self, path=None):
        self.disablePropSelector()
        if self.app.fileManager.load(path):
            self.postLoadUpdate()
        self.enablePropSelector()

    # Clear out all info related to old motor/sim in the interface
    def postLoadUpdate(self):
        self.disablePropSelector() # It is enabled again at the end of updatePropBoxSelection
        self.resetOutput()
        self.updateGrainTable()
        self.populatePropSelector()
        self.updatePropBoxSelection()

    def closeEvent(self, event=None):
        if self.app.fileManager.unsavedCheck():
            sys.exit()
        else:
            if event is not None:
                if not isinstance(event, bool):
                    event.ignore()

    def applyPreferences(self, prefDict):
        self.updateGrainTable()
        self.setupMotorStats()
        self.setupGraph()
