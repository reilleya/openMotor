import motorlib

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox, QComboBox
from PyQt5.QtCore import pyqtSignal

# Todo: read this in from settings instead!
defaultUnits = {'m': 'in', 's':'s', '':''}

class propertyEditor(QWidget):

    valueChanged = pyqtSignal()

    def __init__(self, parent, prop):
        super(propertyEditor, self).__init__(QWidget(parent))
        self.setLayout(QVBoxLayout())
        self.prop = prop

        if type(prop) is motorlib.propellantProperty:
            pass

        elif type(prop) is motorlib.floatProperty:
            self.editor = QDoubleSpinBox()
            self.editor.setValue(motorlib.convert(self.prop.getValue(), prop.unit, defaultUnits[prop.unit]))
            self.editor.setSuffix(' ' + defaultUnits[prop.unit])
            convMin = motorlib.convert(self.prop.min, self.prop.unit, defaultUnits[self.prop.unit])
            convMax = motorlib.convert(self.prop.max, self.prop.unit, defaultUnits[self.prop.unit])
            self.editor.setRange(convMin, convMax)
            self.editor.setDecimals(3)
            self.editor.setSingleStep(0.1)
            self.editor.valueChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif type(prop) is motorlib.intProperty:
            self.editor = QSpinBox()
            self.layout().addWidget(self.editor)

        elif type(prop) is motorlib.enumProperty:
            self.editor = QComboBox()

            self.editor.addItems(self.prop.values)

            self.layout().addWidget(self.editor)


    def getValue(self):
        if type(self.prop) is motorlib.propellantProperty:
            pass

        elif type(self.prop) is motorlib.floatProperty:
            return motorlib.convert(self.editor.value(), defaultUnits[self.prop.unit], self.prop.unit)

        elif type(self.prop) is motorlib.intProperty:
            pass