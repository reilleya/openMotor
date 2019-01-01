import motorlib
from PyQt5.QtWidgets import QWidget, QGroupBox, QLabel, QDoubleSpinBox, QSpinBox, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton

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

class grainEditor(QGroupBox):
    def __init__(self, parent):
        super(grainEditor, self).__init__(QGroupBox(parent))
        self.propertyEditors = {}
        self.setLayout(QVBoxLayout())
        self.form = QFormLayout()
        self.layout().addLayout(self.form)
        self.buttons = QHBoxLayout()
        self.layout().addLayout(self.buttons)

        self.applyButton = QPushButton('Apply')
        self.cancelButton = QPushButton('Cancel')

        self.buttons.addWidget(self.applyButton)
        self.buttons.addWidget(self.cancelButton)

        
    def loadGrain(self, grain):
        self.cleanup()
        for prop in grain.props:
            self.propertyEditors[prop] = grainEditorField(self, grain.props[prop])
            self.form.addRow(QLabel(grain.props[prop].dispName), self.propertyEditors[prop])
            #print(type(grain.props[prop]) is motorlib.floatGrainProperty) 

    def cleanup(self):
        for pid, prop in enumerate(self.propertyEditors):
            self.form.removeRow(0) # Removes the first row, but will delete all by the end of the loop
            del prop
