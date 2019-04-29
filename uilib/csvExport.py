from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QCheckBox, QVBoxLayout
from motorlib import propertyCollection, floatProperty, stringProperty, simulationResult, motor

from . import collectionEditor

class csvExportMenu(QDialog):
    def __init__(self):
        from .views.CSVExporter_ui import Ui_CSVExporter
        QDialog.__init__(self)
        self.ui = Ui_CSVExporter()
        self.ui.setupUi(self)
        self.simRes = None
        self.preferences = None
        self.ui.buttonBox.accepted.connect(self.exportCSV)
        self.checks = {}

        # Populate list of checks to toggle channels
        checkLayout = QVBoxLayout()
        self.ui.groupBoxChecks.setLayout(checkLayout)
        sr = simulationResult(motor()) # This simres is only used to get the list of channels available
        for c in sr.channels:
            check = QCheckBox(sr.channels[c].name)
            check.setCheckState(2) # Every field is checked by default
            if c == "time": # Time must be set
                check.setEnabled(False)
            checkLayout.addWidget(check)
            self.checks[c] = check

    def exportCSV(self):
        exclude = []
        for c in self.checks:
            if not self.checks[c].isChecked():
                exclude.append(c)

        path = QFileDialog.getSaveFileName(None, 'Save CSV', '', 'CSV Files (*.csv)')[0]
        if path is not None and path != '':
            if path[-4:] != '.csv':
                path += '.csv'
            with open(path, 'w') as outFile:
                outFile.write(self.simRes.getCSV(self.preferences, exclude))

    def setPreferences(self, pref):
        self.preferences = pref

    def open(self):
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.simRes is not None)
        for check in self.checks.values(): # Make sure all checks are set when the dialog is reopened
            check.setCheckState(2)
        self.show()

    def acceptSimResult(self, simRes):
        self.simRes = simRes
