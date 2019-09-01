from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

import motorlib

from ..views.PropellantPreview_ui import Ui_PropellantPreview

class PropellantPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PropellantPreview()
        self.ui.setupUi(self)

    def setPreferences(self, pref):
        self.ui.tabBurnRate.setPreferences(pref)

    def loadPropellant(self, propellant):
        self.ui.tabAlerts.clear()
        self.ui.tabBurnRate.cleanup()
        alerts = propellant.getErrors()
        for err in alerts:
            self.ui.tabAlerts.addItem(err.description)

        for alert in alerts:
            if alert.level == motorlib.simResult.SimAlertLevel.ERROR:
                return

        burnrateData = [[], []]
        minPres = int(propellant.getMinimumValidPressure()) + 1 # Add 1 Pa to avoid crashing on burnrate for 0 Pa
        maxPres = int(propellant.getMaximumValidPressure())
        for pres in range(minPres, maxPres, 2000):
            burnrateData[0].append(pres)
            burnrateData[1].append(propellant.getBurnRate(pres))
        self.ui.tabBurnRate.showGraph(burnrateData)

    def cleanup(self):
        self.ui.tabAlerts.clear()
        self.ui.tabBurnRate.cleanup()
