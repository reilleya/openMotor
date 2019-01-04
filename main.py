from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi
import sys

import motorlib

def formatForDisplay(quantity, inUnits, outUnits): # Move to somewhere else
    return str(round(motorlib.convert(quantity, inUnits, outUnits), 3)) + ' ' + outUnits

class Window(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        loadUi("MainWindow.ui", self)

        self.motorStatLabels = [self.labelMotorDesignation, self.labelImpulse, self.labelDeliveredISP, self.labelBurnTime,
                                self.labelAveragePressure, self.labelPeakPressure, self.labelInitialKN, self.labelPeakKN,
                                self.labelPortThroatRatio, self.labelCoreLD, self.labelPeakMassFlux]

        self.loadDefaultMotor()

        self.setupMotorStats()
        self.setupMotorEditor()
        self.setupGrainAddition()
        self.setupMenu()
        self.setupGrainTable()

        self.show()

    def setupMotorStats(self):
        for label in self.motorStatLabels:
            label.setText("-")

    def setupMotorEditor(self):
        self.pushButtonEditGrain.pressed.connect(self.editGrain)
        self.motorEditor.motorChanged.connect(self.updateGrainTable)
        self.motorEditor.closed.connect(self.checkGrainSelection) # Enables only buttons for actions possible given the selected grain

    def setupGrainAddition(self):
        self.comboBoxGrainGeometry.addItems(motorlib.grainTypes.keys())
        self.comboBoxPropellant.addItems(['Cherry Limeade'])
        self.pushButtonAddGrain.pressed.connect(self.addGrain)

    def setupMenu(self):
        #File menu
        self.actionNew.triggered.connect(self.newMotor)
        self.actionQuit.triggered.connect(self.exit)

        #Sim
        self.actionRunSimulation.triggered.connect(self.runSimulation)

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

    def updateGrainTable(self):
        self.tableWidgetGrainList.setRowCount(len(self.motor.grains) + 1)
        for gid, grain in enumerate(self.motor.grains):
            self.tableWidgetGrainList.setItem(gid, 0, QTableWidgetItem(grain.geomName))
            self.tableWidgetGrainList.setItem(gid, 1, QTableWidgetItem(grain.getDetailsString()))

        self.tableWidgetGrainList.setItem(len(self.motor.grains), 0, QTableWidgetItem('Nozzle'))
        self.tableWidgetGrainList.setItem(len(self.motor.grains), 1, QTableWidgetItem(self.motor.nozzle.getDetailsString()))

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
        if len(ind) > 0:
            gid = ind[0].row()
            self.toggleGrainButtons(True)
            if gid == 0: # Top grain selected
                self.pushButtonMoveGrainUp.setEnabled(False)
            if gid == len(self.motor.grains) - 1: # Bottom grain selected
                self.pushButtonMoveGrainDown.setEnabled(False)
            elif gid == len(self.motor.grains):
                self.pushButtonMoveGrainUp.setEnabled(False)
                self.pushButtonMoveGrainDown.setEnabled(False)
                self.pushButtonDeleteGrain.setEnabled(False) 
        else:
            self.toggleGrainEditButtons(False, False)


    def moveGrain(self, offset):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(self.motor.grains) and gid + offset < len(self.motor.grains) and gid + offset >= 0:
                self.motor.grains[gid + offset], self.motor.grains[gid] = self.motor.grains[gid], self.motor.grains[gid + offset]
                self.tableWidgetGrainList.selectRow(gid + offset)
                self.updateGrainTable()

    def editGrain(self):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(self.motor.grains):
                self.motorEditor.loadGrain(self.motor.grains[gid])
            else:
                self.motorEditor.loadNozzle(self.motor.nozzle)
            self.toggleGrainButtons(False)

    def deleteGrain(self):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
        if len(ind) > 0:
            gid = ind[0].row()
            if gid < len(self.motor.grains):
                del self.motor.grains[gid]
                self.updateGrainTable()
                self.checkGrainSelection()


    def addGrain(self):
        newGrain = motorlib.grainTypes[self.comboBoxGrainGeometry.currentText()]()

        newGrain.setProperties({'prop':{ # Todo: should retrieve from propProvider
                    'name': 'Cherry Limeade',
                    'density': 1690, 
                    'a': 3.517054143255937e-05, 
                    'n': 0.3273, 
                    't': 2800, 
                    'm': 23.67, 
                    'k': 1.21}})

        self.motor.grains.append(newGrain)
        self.updateGrainTable()
        self.tableWidgetGrainList.selectRow(len(self.motor.grains) - 1)
        self.checkGrainSelection()

    def updateMotorStats(self, simResult):
        self.labelMotorDesignation.setText(simResult.getDesignation())
        self.labelImpulse.setText(formatForDisplay(simResult.getImpulse(), 'ns', 'lbfs'))
        self.labelDeliveredISP.setText(formatForDisplay(simResult.getISP(), 's', 's'))
        self.labelBurnTime.setText(formatForDisplay(simResult.getBurnTime(), 's', 's'))

        self.labelAveragePressure.setText(formatForDisplay(simResult.getAveragePressure(), 'pa', 'psi'))
        self.labelPeakPressure.setText(formatForDisplay(simResult.getMaxPressure(), 'pa', 'psi'))
        self.labelInitialKN.setText(formatForDisplay(simResult.getInitialKN(), '', ''))
        self.labelPeakKN.setText(formatForDisplay(simResult.getPeakKN(), '', ''))

        self.labelPortThroatRatio.setText(formatForDisplay(simResult.getPortRatio(), '', ''))
        self.labelCoreLD.setText('????')
        self.labelPeakMassFlux.setText(formatForDisplay(simResult.getPeakMassFlux(), 'km/(m^2*s)', 'lb/(in^2*s)'))

    def runSimulation(self):
        self.setupMotorStats()
        simResult = self.motor.runSimulation()
        self.graphWidget.showData(simResult)

        self.updateMotorStats(simResult)

    def newMotor(self):
        #Check for unsaved changes
        self.loadDefaultMotor()
        self.setupMotorStats()
        self.graphWidget.resetPlot()
        self.updateGrainTable()

    def exit(self):
        # Check for unsaved changes
        sys.exit()

    def loadDefaultMotor(self):
        self.motor = motorlib.motor()
        bg = motorlib.batesGrain()
        bg.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.03175, 
                  'inhibitedEnds':0,
                  'prop':{
                    'name': 'Cherry Limeade',
                    'density': 1690, 
                    'a': 3.517054143255937e-05, 
                    'n': 0.3273, 
                    't': 2800, 
                    'm': 23.67, 
                    'k': 1.21}})
        bg2 = motorlib.batesGrain()
        bg2.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.03175, 
                  'inhibitedEnds':0,
                  'prop':{
                    'name': 'Cherry Limeade',
                    'density': 1690, 
                    'a': 3.517054143255937e-05, 
                    'n': 0.3273, 
                    't': 2800, 
                    'm': 23.67, 
                    'k': 1.21}})
        self.motor.grains.append(bg)
        self.motor.grains.append(bg2)

        self.motor.nozzle.setProperties({'throat': 0.015, 'exit': 0.03})

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    sys.exit(app.exec_())