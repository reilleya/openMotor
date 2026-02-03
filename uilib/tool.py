from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout

import motorlib

from .logger import logger
from .widgets.collectionEditor import CollectionEditor


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
        self.changeToBeApplied = None
        # Previously entered value(s), if any
        self.previousValues = None

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
        if self.previousValues is not None:
            self.propCollection.setProperties(self.previousValues)
        self.editor.loadProperties(self.propCollection)
        super().show()

    def applyPressed(self, change):
        logger.log('Applying "{}" from "{}" tool'.format(change, self.name))
        if not self.needsSimulation:
            self.saveValuesAndApplyChanges(change, self.manager.getMotor(), None)
            return

        self.changeToBeApplied = change
        self.motor = self.manager.getMotor()
        self.manager.requestSimulation()

    def simDone(self, sim):
        if self.changeToBeApplied is None:
            return
        # If changeToBeApplied is set, this is the tool waiting for a simulation result
        if sim.success:
            self.saveValuesAndApplyChanges(self.changeToBeApplied, self.motor, sim)
        self.changeToBeApplied = None
        self.motor = None

    def simCanceled(self):
        self.changeToBeApplied = None
        self.motor = None

    def saveValuesAndApplyChanges(self, change, motor, simulation):
        self.previousValues = change
        self.applyChanges(change, motor, simulation)

    def applyChanges(self, change, motor, simulation):
        pass
