from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView
from PyQt5.uic import loadUi
import sys

import motorlib

class GraphWindow(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        loadUi("MainWindow.ui", self)

        self.loadDefaultMotor()

        self.setupGrainEditor()
        self.setupMenu()
        self.setupGrainTable()

        self.show()

    def setupGrainEditor(self):
        self.pushButtonEditGrain.pressed.connect(self.editGrain)

    def setupMenu(self):
        self.actionRunSimulation.triggered.connect(self.runSimulation)

    def setupGrainTable(self):
        self.tableWidgetGrainList.clearContents()

        header = self.tableWidgetGrainList.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.tableWidgetGrainList.setRowCount(len(self.motor.grains))
        for gid, grain in enumerate(self.motor.grains):
            self.tableWidgetGrainList.setItem(gid, 0, QTableWidgetItem(grain.geomName))
            self.tableWidgetGrainList.setItem(gid, 1, QTableWidgetItem(grain.props['prop'].getValue()['name']))
            self.tableWidgetGrainList.setItem(gid, 2, QTableWidgetItem(str(motorlib.convert(grain.props['length'].getValue(), grain.props['length'].unit, 'in')) + " in"))

    def editGrain(self):
        ind = self.tableWidgetGrainList.selectionModel().selectedRows()[0].row()
        self.grainEditor.loadGrain(self.motor.grains[ind])

    def runSimulation(self):
        t, k, p, f, m_flow, m_flux = self.motor.runSimulation()
        self.graphWidget.showData(t, [k, [motorlib.convert(pr, 'mpa', 'psi') for pr in p]])

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
                  'coreDiameter':0.045, 
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
    g = GraphWindow()
    sys.exit(app.exec_())