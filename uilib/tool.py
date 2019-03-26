from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

from . import collectionEditor

import motorlib

class tool(QDialog):
    def __init__(self, manager, name, description, propDict):
        super().__init__()
        self.manager = manager
        self.name = name
        self.description = description
        self.preferences = None
        self.propCollection = motorlib.propertyCollection()
        self.propCollection.props = propDict

        self.setWindowTitle(self.name)
        self.setLayout(QVBoxLayout())

        self.descLabel = QLabel(self.description)
        self.layout().addWidget(self.descLabel)

        self.editor = collectionEditor(self, True)
        self.editor.changeApplied.connect(self.applyChanges)
        self.editor.closed.connect(self.hide)
        self.layout().addWidget(self.editor)

    def setPreferences(self, pref):
        self.preferences = pref
        self.editor.setPreferences(pref)

    def show(self):
        self.editor.loadProperties(self.propCollection)
        super().show()

    def applyChanges(self, inp):
        pass
