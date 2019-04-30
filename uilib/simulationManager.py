from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSignal

from threading import Thread

from motorlib import simAlertLevel, simAlertType, alertLevelNames, alertTypeNames


class simulationProgressDialog(QDialog):

    simulationCanceled = pyqtSignal()

    def __init__(self):
        from .views.SimulatingDialog_ui import Ui_SimProgressDialog
        QDialog.__init__(self)
        self.ui = Ui_SimProgressDialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.rejected.connect(self.closeEvent)

    def show(self):
        self.ui.progressBar.setValue(0)
        super().show()

    def closeEvent(self, event = None):
        self.simulationCanceled.emit()
        self.close()

    def progressUpdate(self, progress):
        self.ui.progressBar.setValue(int(progress * 100))

class simulationAlertsDialog(QDialog):
    def __init__(self):
        from .views.SimulationAlertsDialog_ui import Ui_SimAlertsDialog
        QDialog.__init__(self)
        self.ui = Ui_SimAlertsDialog()
        self.ui.setupUi(self)

        header = self.ui.tableWidgetAlerts.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.hide()

    def displayAlerts(self, simRes):
        self.ui.tableWidgetAlerts.setRowCount(0) # Clear the table
        if len(simRes.alerts) > 0:
            self.ui.tableWidgetAlerts.setRowCount(len(simRes.alerts))
            for row, alert in enumerate(simRes.alerts):
                self.ui.tableWidgetAlerts.setItem(row, 0, QTableWidgetItem(alertLevelNames[alert.level]))
                self.ui.tableWidgetAlerts.setItem(row, 1, QTableWidgetItem(alertTypeNames[alert.type]))
                self.ui.tableWidgetAlerts.setItem(row, 2, QTableWidgetItem(alert.location))
                self.ui.tableWidgetAlerts.setItem(row, 3, QTableWidgetItem(alert.description))
            self.show()


class simulationManager(QObject):

    simulationDone = pyqtSignal(object)
    newSimulationResult = pyqtSignal(object)
    simProgress = pyqtSignal(float)
    simCanceled = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.progDialog = simulationProgressDialog()
        self.simProgress.connect(self.progDialog.progressUpdate)
        self.simulationDone.connect(self.progDialog.hide)
        self.progDialog.simulationCanceled.connect(self.cancelSim)

        self.alertsDialog = simulationAlertsDialog()
        self.simulationDone.connect(self.alertsDialog.displayAlerts)

        self.motor = None
        self.preferences = None

        self.currentSimThread = None
        self.threadStopped = False # Set to true to stop simulation thread after it finishes the iteration it is on

    def setPreferences(self, preferences):
        self.preferences = preferences

    def runSimulation(self, motor, show = True): # Show sets if the results will be reported on newSimulationResult and shown in UI
        self.motor = motor
        self.threadStopped = False
        self.progDialog.show()
        self.currentSimThread = Thread(target = self._simThread, args = [show])
        self.currentSimThread.start()

    def _simThread(self, show):
        simRes = self.motor.runSimulation(self.preferences, self.updateProgressBar)
        self.simulationDone.emit(simRes)
        if simRes.success and show:
            self.newSimulationResult.emit(simRes)

    def updateProgressBar(self, prog):
        self.simProgress.emit(prog)
        return self.threadStopped

    def cancelSim(self):
        self.threadStopped = True
        self.simCanceled.emit()
