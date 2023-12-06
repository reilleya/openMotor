import math

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QCheckBox
from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox, QComboBox
from PyQt6.QtCore import pyqtSignal, Qt

import motorlib

from .polygonEditor import PolygonEditor
from .tabularEditor import TabularEditor

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

        if isinstance(prop, motorlib.properties.FloatProperty):
            self.editor = QDoubleSpinBox()

            self.editor.setSuffix(' {}'.format(self.dispUnit))

            convMin = motorlib.units.convert(self.prop.min, self.prop.unit, self.dispUnit)
            convMax = motorlib.units.convert(self.prop.max, self.prop.unit, self.dispUnit)
            self.editor.setRange(convMin, convMax)

            self.editor.setDecimals(6) # Large number of decimals for now while I pick a better method
            self.editor.setSingleStep(10 ** (int(math.log(convMax, 10) - 4)))

            self.editor.setValue(motorlib.units.convert(self.prop.getValue(), prop.unit, self.dispUnit))
            self.editor.valueChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.IntProperty):
            self.editor = QSpinBox()

            convMin = motorlib.units.convert(self.prop.min, self.prop.unit, self.dispUnit)
            convMax = motorlib.units.convert(self.prop.max, self.prop.unit, self.dispUnit)
            self.editor.setRange(convMin, convMax)

            self.editor.setValue(self.prop.getValue())
            self.editor.valueChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.StringProperty):
            self.editor = QLineEdit()
            self.editor.setText(self.prop.getValue())
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.BooleanProperty):
            self.editor = QCheckBox()
            self.editor.setCheckState(Qt.CheckState.Checked if self.prop.getValue() else Qt.CheckState.Unchecked)
            self.editor.stateChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.EnumProperty):
            self.editor = QComboBox()

            self.editor.addItems(self.prop.values)
            self.editor.setCurrentText(self.prop.value)
            self.editor.currentTextChanged.connect(self.valueChanged.emit)

            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.PolygonProperty):
            self.editor = PolygonEditor(self)

            self.editor.pointsChanged.connect(self.valueChanged.emit)
            self.editor.points = self.prop.getValue()
            self.editor.preferences = self.preferences

            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.TabularProperty):
            self.editor = TabularEditor()

            self.editor.setPreferences(self.preferences)
            for tab in prop.tabs:
                self.editor.addTab(tab)
            self.editor.updated.connect(self.valueChanged.emit)

            self.layout().addWidget(self.editor)

    def getValue(self):
        if isinstance(self.prop, motorlib.properties.FloatProperty):
            return motorlib.units.convert(self.editor.value(), self.dispUnit, self.prop.unit)

        if isinstance(self.prop, motorlib.properties.IntProperty):
            return motorlib.units.convert(self.editor.value(), self.dispUnit, self.prop.unit)

        if isinstance(self.prop, motorlib.properties.StringProperty):
            return self.editor.text()

        if isinstance(self.prop, motorlib.properties.BooleanProperty):
            return self.editor.isChecked()

        if isinstance(self.prop, motorlib.properties.EnumProperty):
            return self.editor.currentText()

        if isinstance(self.prop, motorlib.properties.PolygonProperty):
            return self.editor.points

        if isinstance(self.prop, motorlib.properties.TabularProperty):
            return self.editor.getTabs()

        return None
