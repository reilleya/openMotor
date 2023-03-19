from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PyQt6.QtGui import QIcon

import motorlib

from .widgets.collectionEditor import CollectionEditor
from .logger import logger

class Tool(QDialog):
    def __init__(self, manager, name, description, propDict, needsSimulation):
        super().__init__()
        self.manager = manager
        self.name = name
        self.description = description
        self.needsSimulation = needsSimulation
        self.preferences = None
        self.propCollection = motorlib.properties.PropertyCollection()
        self.propCollection.props = propDict

        self.motor = None
        self.changeApplied = None

        self.setWindowTitle(self.name)
        self.setWindowIcon(QApplication.instance().icon)
        self.setLayout(QVBoxLayout())

        self.descLabel = QLabel(self.description)
        self.descLabel.setWordWrap(True)
        self.layout().addWidget(self.descLabel)

        self.editor = CollectionEditor(self, True)
        self.editor.changeApplied.connect(self.applyPressed)
        self.editor.closed.connect(self.hide)
        self.layout().addWidget(self.editor)

    def setPreferences(self, pref):
        self.preferences = pref
        self.editor.setPreferences(pref)

    def show(self):
        logger.log('Showing "{}" tool'.format(self.name))
        self.editor.loadProperties(self.propCollection)
        super().show()

    def applyPressed(self, change):
        logger.log('Applying "{}" from "{}" tool'.format(change, self.name))
        if not self.needsSimulation:
            self.applyChanges(change, self.manager.getMotor(), None)
            return

        self.changeApplied = change
        self.motor = self.manager.getMotor()
        self.manager.requestSimulation()

    def simDone(self, sim):
        if self.changeApplied is None:
            return
        # If changeApplied is set, this is the tool waiting for a simulation result
        if sim.success:
            self.applyChanges(self.changeApplied, self.motor, sim)
        self.changeApplied = None
        self.motor = None

    def simCanceled(self):
        self.changeApplied = None
        self.motor = None

    def applyChanges(self, change, motor, simulation):
        pass
