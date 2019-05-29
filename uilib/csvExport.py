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

        self.ui.channelSelector.setupChecks(True, disabled = ["time"])

    def exportCSV(self):
        exclude = self.ui.channelSelector.getUnselectedChannels()

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
        self.show()

    def acceptSimResult(self, simRes):
        self.simRes = simRes
