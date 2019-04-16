from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

class aboutDialog(QDialog):
    def __init__(self, version):
        QDialog.__init__(self)
        loadUi("resources/AboutDialog.ui", self)
        self.labelText.setText(self.labelText.text().replace('###', version))
