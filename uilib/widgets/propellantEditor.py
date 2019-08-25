from PyQt5.QtWidgets import QLabel

from motorlib.units import convert
from motorlib.propellant import Propellant
from .collectionEditor import CollectionEditor
from .burnrateGraph import BurnrateGraph

class PropellantEditor(CollectionEditor):
    def __init__(self, parent):
        super().__init__(parent, False)

        self.burnrateGraph = BurnrateGraph()
        self.burnrateGraph.hide()
        self.stats.addWidget(self.burnrateGraph)

    def cleanup(self):
        self.burnrateGraph.hide()
        super().cleanup()

    def setPreferences(self, pref):
        super().setPreferences(pref)
        self.burnrateGraph.setPreferences(self.preferences)

    def propertyUpdate(self):
        previewProp = Propellant(self.getProperties())
        burnrateData = [[], []]

        minPres = int(previewProp.getMinimumValidPressure()) + 1 # Add 1 Pa to avoid crashing on burnrate for 0 Pa
        maxPres = int(previewProp.getMaximumValidPressure())
        for pres in range(minPres, maxPres, 2000):
            burnrateData[0].append(pres)
            burnrateData[1].append(previewProp.getBurnRate(pres))
        self.burnrateGraph.cleanup()
        self.burnrateGraph.showGraph(burnrateData)

    def loadProperties(self, obj):
        super().loadProperties(obj)
        self.burnrateGraph.show()
