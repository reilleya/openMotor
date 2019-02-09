from . import propertyEditor
from . import collectionEditor

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

        self.nozzle = True

    def update(self):
        if self.nozzle:
            exit = self.propertyEditors['exit'].getValue()
            throat = self.propertyEditors['throat'].getValue()
            if throat == 0:
                self.expRatioLabel.setText('Expansion ratio: -')
            else:
                self.expRatioLabel.setText('Expansion ratio: ' + str((exit / throat) ** 2))

    def loadGrain(self, grain):
        self.nozzle = False
        self.loadProperties(grain)

    def loadNozzle(self, nozzle):
        self.nozzle = True
        self.loadProperties(nozzle)
        self.expRatioLabel.show()

    def cleanup(self):
        if self.nozzle:
            self.expRatioLabel.hide()

        super().cleanup()
    