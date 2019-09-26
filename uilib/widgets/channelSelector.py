from PyQt5.QtWidgets import QGroupBox, QCheckBox, QRadioButton, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

import motorlib

class ChannelSelector(QGroupBox):

    checksChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.checks = {}
        # Populate list of checks to toggle channels
        self.setLayout(QVBoxLayout())

    def setupChecks(self, multiselect, disabled=[], default=None, exclude=[]):
        # This simres is only used to get the list of channels available
        simres = motorlib.simResult.SimulationResult(motorlib.motor.Motor())
        for channel in simres.channels:
            if channel not in exclude:
                if multiselect:
                    check = QCheckBox(simres.channels[channel].name)
                else:
                    check = QRadioButton(simres.channels[channel].name)
                self.layout().addWidget(check)
                self.checks[channel] = check
                if default is not None:
                    if multiselect:
                        if channel in default:
                            self.checks[channel].setCheckState(2)
                    else:
                        self.checks[channel].setChecked(channel == default)
                self.checks[channel].toggled.connect(self.checksChanged.emit)
                if channel in disabled:
                    check.setEnabled(False)

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

    def resetChecks(self):
        for check in self.checks:
            self.layout().removeWidget(self.checks[check])
        self.checks = {}

    def unselect(self, channels):
        for channel in channels:
            self.checks[channel].setCheckState(0)

    def toggleEnabled(self, channels, enabled):
        for channel in channels:
            self.checks[channel].setEnabled(enabled)