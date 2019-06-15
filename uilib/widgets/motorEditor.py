from PyQt5.QtWidgets import QLabel, QListWidget, QSizePolicy

import motorlib.grain
import motorlib.nozzle
import motorlib.motor

from .collectionEditor import CollectionEditor
from .grainPreviewWidget import GrainPreviewWidget

class MotorEditor(CollectionEditor):
    def __init__(self, parent):
        super().__init__(parent, True)

        self.expRatioLabel = QLabel("Expansion ratio: -")
        self.expRatioLabel.hide()
        self.stats.addWidget(self.expRatioLabel)

        self.grainPreview = GrainPreviewWidget()
        self.grainPreview.hide()
        self.stats.addWidget(self.grainPreview)

        self.geometryErrorList = QListWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.geometryErrorList.setSizePolicy(sizePolicy)
        self.geometryErrorList.setMaximumWidth(330)
        self.geometryErrorList.setMaximumHeight(100)
        self.geometryErrorList.hide()
        self.stats.addWidget(self.geometryErrorList)

        self.nozzle = True
        self.grainClass = None

    def propertyUpdate(self):
        if issubclass(self.objType, motorlib.nozzle.Nozzle):
            exitDia = self.propertyEditors['exit'].getValue()
            throatDia = self.propertyEditors['throat'].getValue()
            if throatDia == 0:
                self.expRatioLabel.setText('Expansion ratio: -')
            else:
                self.expRatioLabel.setText('Expansion ratio: ' + str(round((exitDia / throatDia) ** 2, 3)))
            testNozzle = self.objType()
            testNozzle.setProperties(self.getProperties())
            self.geometryErrorList.clear()
            for err in testNozzle.getGeometryErrors():
                self.geometryErrorList.addItem(err.description)

        if issubclass(self.objType, motorlib.grain.PerforatedGrain):
            testGrain = self.objType()
            testGrain.setProperties(self.getProperties())
            self.geometryErrorList.clear()
            for err in testGrain.getGeometryErrors():
                self.geometryErrorList.addItem(err.description)
            self.grainPreview.loadGrain(testGrain)

    def loadObject(self, obj):
        self.objType = type(obj)
        self.loadProperties(obj)

        if issubclass(self.objType, motorlib.grain.PerforatedGrain):
            self.grainPreview.show()
            self.geometryErrorList.show()
            self.expRatioLabel.hide()
            self.propertyUpdate()

        if issubclass(self.objType, motorlib.nozzle.Nozzle):
            self.expRatioLabel.show()
            self.geometryErrorList.show()
            self.grainPreview.hide()

        if issubclass(self.objType, motorlib.motor.MotorConfig):
            self.expRatioLabel.hide()
            self.geometryErrorList.hide()
            self.grainPreview.hide()

    def cleanup(self):
        self.expRatioLabel.hide()
        self.geometryErrorList.hide()
        self.grainPreview.hide()
        self.grainPreview.cleanup()
        super().cleanup()
