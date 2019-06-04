from PyQt5.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal

from .propertyEditor import PropertyEditor


class CollectionEditor(QWidget):

    changeApplied = pyqtSignal(dict)
    closed = pyqtSignal()

    def __init__(self, parent, buttons=False):
        super(CollectionEditor, self).__init__(QWidget(parent))

        self.preferences = None


        self.propertyEditors = {}
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)

        self.form = QFormLayout()
        self.layout().addLayout(self.form)

        self.stats = QVBoxLayout()
        self.layout().addLayout(self.stats)


        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout().addItem(self.verticalSpacer)

        self.buttons = buttons
        if self.buttons:
            self.buttons = QHBoxLayout()
            self.layout().addLayout(self.buttons)

            self.applyButton = QPushButton('Apply')
            self.applyButton.pressed.connect(self.apply)
            self.applyButton.hide()

            self.cancelButton = QPushButton('Cancel')
            self.cancelButton.pressed.connect(self.close)
            self.cancelButton.hide()

            self.buttons.addWidget(self.applyButton)
            self.buttons.addWidget(self.cancelButton)

    def propertyUpdate(self):
        pass

    def close(self):
        self.closed.emit()
        self.cleanup()

    def apply(self):
        res = self.getProperties()
        self.cleanup()
        self.changeApplied.emit(res)
        self.closed.emit()

    def setPreferences(self, pref):
        self.preferences = pref

    def loadProperties(self, obj):
        self.cleanup()
        for prop in obj.props:
            self.propertyEditors[prop] = PropertyEditor(self, obj.props[prop], self.preferences)
            self.propertyEditors[prop].valueChanged.connect(self.propertyUpdate)
            label = QLabel(obj.props[prop].dispName + ':')
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.form.addRow(label, self.propertyEditors[prop])
        if self.buttons:
            self.applyButton.show()
            self.cancelButton.show()
        self.propertyUpdate()

    def cleanup(self):
        for prop in self.propertyEditors:
            self.form.removeRow(0) # Removes the first row, but will delete all by the end of the loop
        self.propertyEditors = {}

        if self.buttons:
            self.applyButton.hide()
            self.cancelButton.hide()
        self.repaint()

    def getProperties(self):
        res = {}
        for prop in self.propertyEditors:
            out = self.propertyEditors[prop].getValue()
            if out is not None:
                res[prop] = out
        return res
