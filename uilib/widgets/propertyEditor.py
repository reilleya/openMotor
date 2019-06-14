import math

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox, QComboBox
from PyQt5.QtCore import pyqtSignal

import motorlib

from .polygonEditor import PolygonEditor


class PropertyEditor(QWidget):

    valueChanged = pyqtSignal()

    def __init__(self, parent, prop, preferences):
        super(PropertyEditor, self).__init__(QWidget(parent))
        self.preferences = preferences
        self.setLayout(QVBoxLayout())
        self.prop = prop

        if self.preferences is not None:
            self.dispUnit = self.preferences.getUnit(self.prop.unit)
        else:
            self.dispUnit = self.prop.unit

        if isinstance(prop, motorlib.properties.floatProperty):
            self.editor = QDoubleSpinBox()

            self.editor.setSuffix(' ' + self.dispUnit)

            convMin = motorlib.units.convert(self.prop.min, self.prop.unit, self.dispUnit)
            convMax = motorlib.units.convert(self.prop.max, self.prop.unit, self.dispUnit)
            self.editor.setRange(convMin, convMax)

            self.editor.setDecimals(6) # Large number of decimals for now while I pick a better method
            self.editor.setSingleStep(10 ** (int(math.log(convMax, 10) - 4)))

            self.editor.setValue(motorlib.units.convert(self.prop.getValue(), prop.unit, self.dispUnit))
            self.editor.valueChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.intProperty):
            self.editor = QSpinBox()

            convMin = motorlib.units.convert(self.prop.min, self.prop.unit, self.dispUnit)
            convMax = motorlib.units.convert(self.prop.max, self.prop.unit, self.dispUnit)
            self.editor.setRange(convMin, convMax)

            self.editor.setValue(self.prop.getValue())
            self.editor.valueChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.stringProperty):
            self.editor = QLineEdit()
            self.editor.setText(self.prop.getValue())
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.enumProperty):
            self.editor = QComboBox()

            self.editor.addItems(self.prop.values)
            self.editor.setCurrentText(self.prop.value)
            self.editor.currentTextChanged.connect(self.valueChanged.emit)

            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.polygonProperty):
            self.editor = PolygonEditor(self)

            self.editor.pointsChanged.connect(self.valueChanged.emit)
            self.editor.points = self.prop.getValue()
            self.editor.preferences = self.preferences

            self.layout().addWidget(self.editor)

    def getValue(self):
        if isinstance(self.prop, motorlib.properties.floatProperty):
            return motorlib.units.convert(self.editor.value(), self.dispUnit, self.prop.unit)

        if isinstance(self.prop, motorlib.properties.intProperty):
            return motorlib.units.convert(self.editor.value(), self.dispUnit, self.prop.unit)

        if isinstance(self.prop, motorlib.properties.stringProperty):
            return self.editor.text()

        if isinstance(self.prop, motorlib.properties.enumProperty):
            return self.editor.currentText()

        if isinstance(self.prop, motorlib.properties.polygonProperty):
            return self.editor.points

        return None
