from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import pyqtSignal

from .tools import *

class ToolManager(QObject):

    changeApplied = pyqtSignal()

    def __init__(self, fileManager, simulationManager, propellantManager):
        super().__init__()

        self.fileManager = fileManager
        self.simulationManager = simulationManager
        self.propellantManager = propellantManager

        self.tools = {'Set': [ChangeDiameterTool(self), InitialKNTool(self), MaxKNTool(self)],
                      'Optimize': [ExpansionTool(self)],
                      'Design': [NeutralBatesTool(self)]}

        for toolCategory in self.tools:
            for toolToAdd in self.tools[toolCategory]:
                self.simulationManager.simulationDone.connect(toolToAdd.simDone)
                self.simulationManager.simCanceled.connect(toolToAdd.simCanceled)

    def setPreferences(self, pref):
        for toolCategory in self.tools:
            for toolToSet in self.tools[toolCategory]:
                toolToSet.setPreferences(pref)

    def setupMenu(self, menu):
        for toolCategory in self.tools:
            category = menu.addMenu(toolCategory)
            for toolToSetup in self.tools[toolCategory]:
                toolAction = QAction(toolToSetup.name, category)
                toolAction.setStatusTip(toolToSetup.description)
                toolAction.triggered.connect(toolToSetup.show)
                category.addAction(toolAction)

    def getMotor(self):
        return self.fileManager.getCurrentMotor()

    def getPropellantNames(self):
        return self.propellantManager.getNames()

    def getPropellantByName(self, name):
        return self.propellantManager.getPropellantByName(name)

    def updateMotor(self, motor):
        self.fileManager.addNewMotorHistory(motor)
        self.changeApplied.emit()

    def requestSimulation(self):
        motor = self.fileManager.getCurrentMotor()
        self.simulationManager.runSimulation(motor, False)
