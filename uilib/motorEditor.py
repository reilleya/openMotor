from . import propertyEditor

from PyQt5.QtWidgets import QWidget, QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox, QLabel, QPushButton
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal

class motorEditor(QGroupBox):

    motorChanged = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, parent):
        super(motorEditor, self).__init__(QGroupBox(parent))

        self.preferences = None

        self.propertyEditors = {}
        self.setLayout(QVBoxLayout())
        self.form = QFormLayout()
        self.layout().addLayout(self.form)

        self.stats = QVBoxLayout()
        self.layout().addLayout(self.stats)
        self.expRatioLabel = QLabel("Expansion ratio: -")
        self.expRatioLabel.hide()
        self.stats.addWidget(self.expRatioLabel)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout().addItem(self.verticalSpacer)

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

        self.nozzle = None
        self.grain = None
        
    def setPreferences(self, pref):
        self.preferences = pref

    def loadProperties(self, object):
        self.cleanup()
        for prop in object.props:
            self.propertyEditors[prop] = propertyEditor(self, object.props[prop], self.preferences)
            self.propertyEditors[prop].valueChanged.connect(self.update)
            self.form.addRow(QLabel(object.props[prop].dispName), self.propertyEditors[prop])

    def loadGrain(self, grain):
        self.loadProperties(grain)
        self.grain = grain
        self.applyButton.show()
        self.cancelButton.show()

    def loadNozzle(self, nozzle):
        self.loadProperties(nozzle)
        self.nozzle = nozzle
        self.update()
        self.expRatioLabel.show()
        self.applyButton.show()
        self.cancelButton.show()

    def close(self):
        self.closed.emit()
        self.cleanup()

    def cleanup(self):
        if self.grain is not None:
            self.grain = None
        elif self.nozzle is not None:
            self.nozzle = None
            self.expRatioLabel.hide()

        for prop in self.propertyEditors:
            self.form.removeRow(0) # Removes the first row, but will delete all by the end of the loop
        self.propertyEditors = {}

        self.applyButton.hide()
        self.cancelButton.hide()

    def apply(self):
        res = {}
        for prop in self.propertyEditors:
            out = self.propertyEditors[prop].getValue()
            if out is not None:
                res[prop] = out
        if self.grain is not None:
            self.grain.setProperties(res)
        elif self.nozzle is not None:
            self.nozzle.setProperties(res)
        self.motorChanged.emit()
        self.closed.emit()
        self.cleanup()

    def update(self):
        if self.nozzle is not None:
            exit = self.propertyEditors['exit'].getValue()
            throat = self.propertyEditors['throat'].getValue()
            if throat == 0:
                self.expRatioLabel.setText('Expansion ratio: -')
            else:
                self.expRatioLabel.setText('Expansion ratio: ' + str((exit / throat) ** 2))