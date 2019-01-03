import motorlib
from PyQt5.QtWidgets import QWidget, QGroupBox, QLabel, QDoubleSpinBox, QSpinBox, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal

inputUnit = 'in'

class grainEditorField(QWidget):
    def __init__(self, parent, prop):
        super(grainEditorField, self).__init__(QWidget(parent))
        self.setLayout(QVBoxLayout())
        self.prop = prop

        if type(prop) is motorlib.propellantGrainProperty:
            pass

        elif type(prop) is motorlib.floatGrainProperty:
            self.editor = QDoubleSpinBox()
            self.editor.setValue(motorlib.convert(self.prop.getValue(), prop.unit, inputUnit))
            self.editor.setSuffix(' ' + inputUnit)
            self.layout().addWidget(self.editor)

        elif type(prop) is motorlib.intGrainProperty:
            self.layout().addWidget(QSpinBox())

    def getValue(self):
        if type(self.prop) is motorlib.propellantGrainProperty:
            pass

        elif type(self.prop) is motorlib.floatGrainProperty:
            return motorlib.convert(self.editor.value(), inputUnit, self.prop.unit)

        elif type(self.prop) is motorlib.intGrainProperty:
            pass

class motorEditor(QGroupBox):

    motorChanged = pyqtSignal()

    def __init__(self, parent):
        super(motorEditor, self).__init__(QGroupBox(parent))
        self.propertyEditors = {}
        self.setLayout(QVBoxLayout())
        self.form = QFormLayout()
        self.layout().addLayout(self.form)
        self.buttons = QHBoxLayout()
        self.layout().addLayout(self.buttons)

        self.applyButton = QPushButton('Apply')
        self.applyButton.pressed.connect(self.apply)
        self.applyButton.hide()

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.pressed.connect(self.cleanup)
        self.cancelButton.hide()

        self.buttons.addWidget(self.applyButton)
        self.buttons.addWidget(self.cancelButton)

        
    def loadGrain(self, grain):
        self.cleanup()
        self.grain = grain
        for prop in grain.props:
            self.propertyEditors[prop] = grainEditorField(self, grain.props[prop])
            self.form.addRow(QLabel(grain.props[prop].dispName), self.propertyEditors[prop])
        self.applyButton.show()
        self.cancelButton.show()

    def cleanup(self):
        self.grain = None
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
        self.grain.setProperties(res)
        self.motorChanged.emit()
        self.cleanup()