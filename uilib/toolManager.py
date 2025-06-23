from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QAction

from .tools import ChangeDiameterTool, InitialKNTool, MaxKNTool, MaxPressureTool
from .tools import ExpansionTool
from .tools import NeutralBatesTool
from .logger import logger

class ToolManager(QObject):

    changeApplied = pyqtSignal()

    def __init__(self, app):
        super().__init__()

        self.fileManager = app.fileManager
        self.simulationManager = app.simulationManager
        self.propellantManager = app.propellantManager

        self.tools = {'Set': [
                                ChangeDiameterTool(self),
                                InitialKNTool(self),
                                MaxKNTool(self),
                                MaxPressureTool(self)
                            ],
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
        logger.log('Tool applied change to motor')

    def requestSimulation(self):
        logger.log('Tool requested simulation')
        motor = self.fileManager.getCurrentMotor()
        self.simulationManager.runSimulation(motor, False)
