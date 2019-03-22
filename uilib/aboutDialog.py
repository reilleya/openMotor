from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

class aboutDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        loadUi("resources/AboutDialog.ui", self)
