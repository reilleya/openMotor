from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from motorlib import propertyCollection

class preferences():
    def __init__(self):
        self.s = 0


class PreferencesWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        loadUi("Preferences.ui", self)
        self.buttonBox.accepted.connect(self.apply)
        self.buttonBox.rejected.connect(self.cancel)

    def apply(self):
        self.hide()

    def cancel(self):
        self.hide()