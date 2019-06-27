from PyQt5.QtWidgets import QGroupBox, QCheckBox, QRadioButton, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

import motorlib

class GrainSelector(QGroupBox):

    checksChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.checks = []
        self.setLayout(QVBoxLayout())
        self.setTitle("Grains")

    def resetChecks(self):
        for check in range(0, len(self.checks)):
            self.layout().removeWidget(self.checks[-1])
            self.checks[-1].deleteLater()
            del self.checks[-1]

    def setupChecks(self, simRes, multiselect):
        for gid, grain in enumerate(simRes.motor.grains):
            checkTitle = "Grain " + str(gid + 1)
            if multiselect:
                check = QCheckBox(checkTitle)
                check.setCheckState(2)
            else:
                check = QRadioButton(checkTitle)
            self.layout().addWidget(check)
            self.checks.append(check)
            self.checks[-1].toggled.connect(self.checksChanged.emit)

    def getSelectedGrains(self):
        selected = []
        for checkId, check in enumerate(self.checks):
            if check.isChecked():
                selected.append(checkId)
        return selected

    def getUnselectedGrains(self):
        selected = []
        for checkId, check in enumerate(self.checks):
            if not check.isChecked():
                selected.append(checkId)
        return selected
