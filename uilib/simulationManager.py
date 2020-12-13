from threading import Thread

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from .widgets.simulationAlertsDialog import SimulationAlertsDialog
from .widgets.simulationProgressDialog import SimulationProgressDialog
from .logger import logger

class SimulationManager(QObject):

    simulationDone = pyqtSignal(object)
    newSimulationResult = pyqtSignal(object)
    simProgress = pyqtSignal(float)
    simCanceled = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.progDialog = SimulationProgressDialog()
        self.simProgress.connect(self.progDialog.progressUpdate)
        self.simulationDone.connect(self.progDialog.hide)
        self.progDialog.simulationCanceled.connect(self.cancelSim)

        self.alertsDialog = SimulationAlertsDialog()
        self.simulationDone.connect(self.alertsDialog.displayAlerts)

        self.motor = None
        self.preferences = None

        self.currentSimThread = None
        self.threadStopped = False # Set to true to stop simulation thread after it finishes the iteration it is on

    def setPreferences(self, preferences):
        self.preferences = preferences

    def runSimulation(self, motor, show=True): # Show sets if the results will be reported on newSimulationResult and shown in UI
        logger.log('Running simulation')
        self.motor = motor
        self.threadStopped = False
        self.progDialog.show()
        self.currentSimThread = Thread(target=self._simThread, args=[show])
        self.currentSimThread.start()

    def _simThread(self, show):
        simRes = self.motor.runSimulation(self.updateProgressBar)
        self.simulationDone.emit(simRes)
        if simRes.success and show:
            logger.log('Simulation succeeded')
            self.newSimulationResult.emit(simRes)

    def updateProgressBar(self, prog):
        self.simProgress.emit(prog)
        return self.threadStopped

    def cancelSim(self):
        logger.log('Canceling simulation')
        self.threadStopped = True
        self.simCanceled.emit()
