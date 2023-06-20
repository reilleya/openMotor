from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal

from motorlib.enums.unit import Unit
from motorlib.units import convert
from motorlib.propellant import PropellantTab
from motorlib.constants import gasConstant

from .collectionEditor import CollectionEditor

class PropellantTabEditor(CollectionEditor):

    modified = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent, False)

        self.labelCStar = QLabel("Characteristic Velocity: -")
        self.labelCStar.hide()
        self.stats.addWidget(self.labelCStar)

    def propertyUpdate(self):
        k = self.propertyEditors['k'].getValue()
        t = self.propertyEditors['t'].getValue()
        m = self.propertyEditors['m'].getValue()
        num = (k * gasConstant / m * t) ** 0.5
        denom = k * ((2 / (k + 1)) ** ((k + 1) / (k - 1))) ** 0.5
        charVel = num / denom

        if self.preferences is not None:
            dispUnit = self.preferences.getUnit(Unit.METER_PER_SECOND)
        else:
            dispUnit = Unit.METER_PER_SECOND

        cStarText = '{} {}'.format(int(convert(charVel, Unit.METER_PER_SECOND, dispUnit)), dispUnit)

        self.labelCStar.setText('Characteristic Velocity: {}'.format(cStarText))
        self.modified.emit()

    def cleanup(self):
        self.labelCStar.hide()
        super().cleanup()

    def getProperties(self): # Override to change units on ballistic coefficient
        res = super().getProperties()
        coeffUnit = self.propertyEditors['a'].dispUnit
        if coeffUnit == Unit.INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N:
            res['a'] *= 1 / (6895 ** res['n'])
        return res

    def loadProperties(self, obj): # Override for ballistic coefficient units
        props = obj.getProperties()
        # Convert the ballistic coefficient based on the exponent
        ballisticCoeffUnit = self.preferences.getUnit(Unit.METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N)
        if ballisticCoeffUnit == Unit.INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N:
            props['a'] /= 1 / (6895 ** props['n'])
        # Create a new propellant instance using the new A
        newPropTab = PropellantTab()
        newPropTab.setProperties(props)
        super().loadProperties(newPropTab)
        self.labelCStar.show()
