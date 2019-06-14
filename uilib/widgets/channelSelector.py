from PyQt5.QtWidgets import QGroupBox, QCheckBox, QRadioButton, QVBoxLayout

import motorlib

class ChannelSelector(QGroupBox):
    def __init__(self, parent):
        super().__init__(parent)

        self.checks = {}
        # Populate list of checks to toggle channels
        self.setLayout(QVBoxLayout())

    def setupChecks(self, multiselect, disabled=[]):
        # This simres is only used to get the list of channels available
        simres = motorlib.simResult.simulationResult(motorlib.motor.Motor())
        for channel in simres.channels:
            if multiselect:
                check = QCheckBox(simres.channels[channel].name)
                check.setCheckState(2) # Every field is checked by default
            else:
                check = QRadioButton(simres.channels[channel].name)
            if channel in disabled:
                check.setEnabled(False)
            self.layout().addWidget(check)
            self.checks[channel] = check

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
