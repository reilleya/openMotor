from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from PyQt5.uic import loadUi
from motorlib import propertyCollection, floatProperty, stringProperty
from . import collectionEditor

class csvExportMenu(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        loadUi('resources/CSVExporter.ui', self)
        self.simRes = None
        self.preferences = None
        self.buttonBox.accepted.connect(self.exportCSV)

    def exportCSV(self):
        path = QFileDialog.getSaveFileName(None, 'Save CSV', '', 'CSV Files (*.csv)')[0]
        if path is not None and path != '':
            if path[-4:] != '.csv':
                path += '.csv'

            with open(path, 'w') as outFile:
                outFile.write(self.simRes.getCSV(self.preferences))

    def setPreferences(self, pref):
        self.preferences = pref

    def open(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.simRes is not None)
        self.show()

    def acceptSimResult(self, simRes):
        self.simRes = simRes
