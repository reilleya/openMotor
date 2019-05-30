from PyQt5.QtWidgets import QGroupBox, QCheckBox, QRadioButton, QVBoxLayout
from motorlib import propertyCollection, simulationResult, motor

class ChannelSelector(QGroupBox):
    def __init__(self, parent, multiselect = True):
        super().__init__(parent)

        self.checks = {}
        # Populate list of checks to toggle channels
        self.setLayout(QVBoxLayout())

    def setupChecks(self, multiselect, disabled = []):
        sr = simulationResult(motor()) # This simres is only used to get the list of channels available
        for c in sr.channels:
            if multiselect:
                check = QCheckBox(sr.channels[c].name)
                check.setCheckState(2) # Every field is checked by default
            else:
                check = QRadioButton(sr.channels[c].name)
            if c in disabled:
                check.setEnabled(False)
            self.layout().addWidget(check)
            self.checks[c] = check

    def getSelectedChannels(self):
        selected = []
        for check in self.checks:
            if self.checks[check].isChecked():
                selected.append(check)
        return selected

    def getUnselectedChannels(self):
        selected = []
        for check in self.checks:
            if not self.checks[check].isChecked():
                selected.append(check)
        return selected
