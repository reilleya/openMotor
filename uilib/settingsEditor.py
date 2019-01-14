from . import propertyEditor

from PyQt5.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal

class settingsEditor(QWidget):
    def __init__(self, parent):
        super(settingsEditor, self).__init__(QWidget(parent))

        self.preferences = None

        self.propertyEditors = {}
        self.setLayout(QVBoxLayout())
        self.form = QFormLayout()
        self.layout().addLayout(self.form)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout().addItem(self.verticalSpacer)
        
    def setPreferences(self, pref):
        self.preferences = pref

    def loadProperties(self, object):
        self.cleanup()
        for prop in object.props:
            self.propertyEditors[prop] = propertyEditor(self, object.props[prop], self.preferences)
            self.form.addRow(QLabel(object.props[prop].dispName + ':'), self.propertyEditors[prop])

    def cleanup(self):
        for prop in self.propertyEditors:
            self.form.removeRow(0) # Removes the first row, but will delete all by the end of the loop
        self.propertyEditors = {}

    def getProperties(self):
        res = {}
        for prop in self.propertyEditors:
            out = self.propertyEditors[prop].getValue()
            if out is not None:
                res[prop] = out
        self.cleanup()
        return res