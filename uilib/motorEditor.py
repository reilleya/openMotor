from . import propertyEditor
from . import collectionEditor
from . import grainPreviewWidget

from motorlib import perforatedGrain

from PyQt5.QtWidgets import QWidget, QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox, QLabel, QPushButton
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal

class motorEditor(collectionEditor):
    def __init__(self, parent):
        super().__init__(parent, True)

        self.expRatioLabel = QLabel("Expansion ratio: -")
        self.expRatioLabel.hide()
        self.stats.addWidget(self.expRatioLabel)

        self.grainPreview = grainPreviewWidget()
        self.grainPreview.hide()
        self.stats.addWidget(self.grainPreview)

        self.nozzle = True
        self.grainClass = None

    def propertyUpdate(self):
        if self.nozzle:
            exit = self.propertyEditors['exit'].getValue()
            throat = self.propertyEditors['throat'].getValue()
            if throat == 0:
                self.expRatioLabel.setText('Expansion ratio: -')
            else:
                self.expRatioLabel.setText('Expansion ratio: ' + str((exit / throat) ** 2))

        if self.grainClass is not None:
            testgrain = self.grainClass()
            testgrain.setProperties(self.getProperties())

            self.grainPreview.loadGrain(testgrain)

    def loadGrain(self, grain):
        self.nozzle = False
        self.loadProperties(grain)
        if isinstance(grain, perforatedGrain):
            self.grainClass = type(grain)
            self.grainPreview.show()
            self.propertyUpdate()
        else:
            self.grainClass = None
            self.grainPreview.hide()

    def loadNozzle(self, nozzle):
        self.nozzle = True
        self.grainClass = None
        self.loadProperties(nozzle)
        self.expRatioLabel.show()
        self.grainPreview.hide()

    def cleanup(self):
        if self.nozzle:
            self.expRatioLabel.hide()
        if self.grainClass is not None:
            self.grainPreview.hide()
            self.grainPreview.cleanup()
            self.grainClass = None # Needed so it isn't trying to update the preview grain while loading in properties. Refactor this!
        super().cleanup()
    