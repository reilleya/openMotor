from PyQt6.QtWidgets import QLabel

import motorlib.grain
import motorlib.nozzle
import motorlib.motor

from .collectionEditor import CollectionEditor
from .grainPreviewWidget import GrainPreviewWidget
from .nozzlePreviewWidget import NozzlePreviewWidget

class MotorEditor(CollectionEditor):
    def __init__(self, parent):
        super().__init__(parent, True)

        self.expRatioLabel = QLabel("Expansion ratio: -")
        self.expRatioLabel.hide()
        self.stats.addWidget(self.expRatioLabel)

        self.grainPreview = GrainPreviewWidget()
        self.grainPreview.hide()
        self.stats.addWidget(self.grainPreview)

        self.nozzlePreview = NozzlePreviewWidget()
        self.nozzlePreview.hide()
        self.stats.addWidget(self.nozzlePreview)

        self.objType = None

    def propertyUpdate(self):
        if issubclass(self.objType, motorlib.nozzle.Nozzle):
            exitDia = self.propertyEditors['exit'].getValue()
            throatDia = self.propertyEditors['throat'].getValue()
            if throatDia == 0:
                self.expRatioLabel.setText('Expansion ratio: -')
            else:
                self.expRatioLabel.setText('Expansion ratio: {:.3f}'.format((exitDia / throatDia) ** 2))
            nozzle = self.objType()
            nozzle.setProperties(self.getProperties())
            self.nozzlePreview.loadNozzle(nozzle)

        if issubclass(self.objType, motorlib.grain.PerforatedGrain):
            testGrain = self.objType()
            testGrain.setProperties(self.getProperties())
            self.grainPreview.loadGrain(testGrain)

    def loadObject(self, obj):
        self.objType = type(obj)
        self.loadProperties(obj)

        if issubclass(self.objType, motorlib.grain.PerforatedGrain):
            self.grainPreview.show()
            self.nozzlePreview.hide()
            self.expRatioLabel.hide()
            self.propertyUpdate()

        if issubclass(self.objType, motorlib.nozzle.Nozzle):
            self.expRatioLabel.show()
            self.nozzlePreview.show()
            self.grainPreview.hide()

        if issubclass(self.objType, motorlib.motor.MotorConfig):
            self.expRatioLabel.hide()
            self.nozzlePreview.hide()
            self.grainPreview.hide()

    def cleanup(self):
        self.expRatioLabel.hide()
        self.grainPreview.hide()
        self.nozzlePreview.hide()
        self.grainPreview.cleanup()
        super().cleanup()
