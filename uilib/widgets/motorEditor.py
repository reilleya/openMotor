from PyQt5.QtWidgets import QLabel, QListWidget, QSizePolicy

from motorlib.grain import PerforatedGrain

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
        if self.nozzle:
            exitDia = self.propertyEditors['exit'].getValue()
            throatDia = self.propertyEditors['throat'].getValue()
            if throatDia == 0:
                self.expRatioLabel.setText('Expansion ratio: -')
            else:
                self.expRatioLabel.setText('Expansion ratio: ' + str(round((exitDia / throatDia) ** 2, 3)))

        if self.grainClass is not None:
            testgrain = self.grainClass()
            testgrain.setProperties(self.getProperties())
            self.geometryErrorList.clear()
            for err in testgrain.getGeometryErrors():
                self.geometryErrorList.addItem(err.description)
            self.grainPreview.loadGrain(testgrain)

    def loadGrain(self, grain):
        self.nozzle = False
        self.loadProperties(grain)
        if isinstance(grain, PerforatedGrain):
            self.grainClass = type(grain)
            self.grainPreview.show()
            self.propertyUpdate()
        else:
            self.grainClass = None
            self.grainPreview.hide()
        self.geometryErrorList.show()

    def loadNozzle(self, nozzle):
        self.nozzle = True
        self.grainClass = None
        self.loadProperties(nozzle)
        self.expRatioLabel.show()
        self.grainPreview.hide()
        self.geometryErrorList.hide()

    def loadConfig(self, config):
        self.nozzle = False
        self.grainClass = None
        self.loadProperties(config)
        self.expRatioLabel.hide()
        self.grainPreview.hide()

    def cleanup(self):
        if self.nozzle:
            self.expRatioLabel.hide()
            self.geometryErrorList.hide()
        if self.grainClass is not None:
            self.grainPreview.hide()
            self.grainPreview.cleanup()
            self.geometryErrorList.hide()
            # Needed so it isn't trying to update the preview grain while loading in properties. Refactor this!
            self.grainClass = None
        super().cleanup()
    