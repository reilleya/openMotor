from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView
from PyQt5.uic import loadUi
import sys

import motorlib

def formatForDisplay(quantity, inUnits, outUnits): # Move to somewhere else
    return str(round(motorlib.convert(quantity, inUnits, outUnits), 3)) + ' ' + outUnits

<<<<<<< HEAD
class Window(QMainWindow):
=======
class GraphWindow(QMainWindow):
>>>>>>> c34b6b1a1d1ddcaa218d77e91c2a158083aa0c8b
    def __init__(self):
        QWidget.__init__(self)
        loadUi("MainWindow.ui", self)

        self.motorStatLabels = [self.labelMotorDesignation, self.labelImpulse, self.labelDeliveredISP, self.labelBurnTime,
                                self.labelAveragePressure, self.labelPeakPressure, self.labelInitialKN, self.labelPeakKN,
                                self.labelPortThroatRatio, self.labelCoreLD, self.labelPeakMassFlux]

        self.loadDefaultMotor()

        self.setupMotorStats()
        self.setupGrainEditor()
        self.setupMenu()
        self.setupGrainTable()

        self.show()

    def setupMotorStats(self):
        for label in self.motorStatLabels:
            label.setText("-")

    def setupGrainEditor(self):
        self.pushButtonEditGrain.pressed.connect(self.editGrain)

    def setupMenu(self):
        self.actionRunSimulation.triggered.connect(self.runSimulation)

    def setupGrainTable(self):
        self.tableWidgetGrainList.clearContents()

        header = self.tableWidgetGrainList.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.updateGrainTable()

    def updateGrainTable(self):
        self.tableWidgetGrainList.setRowCount(len(self.motor.grains) + 1)
        for gid, grain in enumerate(self.motor.grains):
            self.tableWidgetGrainList.setItem(gid, 0, QTableWidgetItem(grain.geomName))
            self.tableWidgetGrainList.setItem(gid, 1, QTableWidgetItem(grain.props['prop'].getValue()['name']))

        self.tableWidgetGrainList.setItem(len(self.motor.grains), 0, QTableWidgetItem('Nozzle'))
        self.tableWidgetGrainList.setItem(len(self.motor.grains), 1, QTableWidgetItem('-'))

    def editGrain(self):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()
        if len(ind) > 0:
            self.grainEditor.loadGrain(self.motor.grains[ind[0].row()])

    def updateMotorStats(self, simResult):
        self.labelMotorDesignation.setText(simResult.getDesignation())
        self.labelImpulse.setText(formatForDisplay(simResult.getImpulse(), 'ns', 'ns'))
        self.labelDeliveredISP.setText('??? s')
        self.labelBurnTime.setText(formatForDisplay(simResult.getBurnTime(), 's', 's'))

        self.labelAveragePressure.setText(formatForDisplay(simResult.getAveragePressure(), 'pa', 'psi'))
        self.labelPeakPressure.setText(formatForDisplay(simResult.getMaxPressure(), 'pa', 'psi'))
        self.labelInitialKN.setText(formatForDisplay(simResult.getInitialKN(), '', ''))
        self.labelPeakKN.setText(formatForDisplay(simResult.getPeakKN(), '', ''))

        self.labelPortThroatRatio.setText('????')
        self.labelCoreLD.setText('????')
        self.labelPeakMassFlux.setText(formatForDisplay(simResult.getPeakMassFlux(), 'km/(m^2*s)', 'lb/(in^2*s)'))

    def updateMotorStats(self, simResult):
        self.labelMotorDesignation.setText(simResult.getDesignation())
        self.labelImpulse.setText(formatForDisplay(simResult.getImpulse(), 'ns', 'lbfs'))
        self.labelDeliveredISP.setText('??? s')
        self.labelBurnTime.setText(formatForDisplay(simResult.getBurnTime(), 's', 's'))

        self.labelAveragePressure.setText(formatForDisplay(simResult.getAveragePressure(), 'pa', 'psi'))
        self.labelPeakPressure.setText(formatForDisplay(simResult.getMaxPressure(), 'pa', 'psi'))
        self.labelInitialKN.setText(formatForDisplay(simResult.getInitialKN(), '', ''))
        self.labelPeakKN.setText(formatForDisplay(simResult.getPeakKN(), '', ''))

        self.labelPortThroatRatio.setText('????')
        self.labelCoreLD.setText('????')
        self.labelPeakMassFlux.setText(formatForDisplay(simResult.getPeakMassFlux(), 'km/(m^2*s)', 'lb/(in^2*s)'))

    def runSimulation(self):
        self.setupMotorStats()
        simResult = self.motor.runSimulation()
        self.graphWidget.showData(simResult)

        self.updateMotorStats(simResult)

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
                    't': 2770, 
                    'm': 23.67, 
                    'k': 1.21}})
        bg2 = motorlib.batesGrain()
        bg2.setProperties({'diameter':0.083058, 
                  'length':0.18, 
                  'coreDiameter':0.04, 
                  'inhibitedEnds':0,
                  'prop':{
                    'name': 'Cherry Limeade',
                    'density': 1690, 
                    'a': 3.517054143255937e-05, 
                    'n': 0.3273, 
                    't': 2770, 
                    'm': 23.67, 
                    'k': 1.21}})
        self.motor.grains.append(bg)
        self.motor.grains.append(bg2)
        self.motor.nozzleThroat = 0.015
        self.motor.nozzleExit = 0.015

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    sys.exit(app.exec_())