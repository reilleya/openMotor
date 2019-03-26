from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtCore import pyqtSignal

from .tools import changeDiameterTool

class toolManager(QObject):

    def __init__(self, fileManager):
        super().__init__()

        self.fileManager = fileManager

        self.tools = {'Set': [changeDiameterTool(self)],
                      'Optimize': [],
                      'Design': []}

        self.motor = None

    def setPreferences(self, pref):
        for toolCategory in self.tools.keys():
            for tool in self.tools[toolCategory]:
                tool.setPreferences(pref)

    def setupMenu(self, menu):
        for toolCategory in self.tools.keys():
            category = menu.addMenu(toolCategory)
            for tool in self.tools[toolCategory]:
                toolAction = QAction(tool.name, category)
                toolAction.setStatusTip(tool.description)
                toolAction.triggered.connect(tool.show)
                category.addAction(toolAction)

    def getMotor(self):
        return self.fileManager.getCurrentMotor()

    def updateMotor(self, motor):
        self.fileManager.addNewMotorHistory(motor)
