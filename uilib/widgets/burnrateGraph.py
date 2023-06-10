from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from motorlib.enums.units.PressureUnit import PressureUnit
from motorlib.enums.units.VelocityUnit import VelocityUnit
from motorlib.units import convertAll

class BurnrateGraph(FigureCanvas):
    def __init__(self):
        super(BurnrateGraph, self).__init__(Figure())
        self.setParent(None)
        self.preferences = None

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.tight_layout()

        self.plot = self.figure.add_subplot(111)

    def setPreferences(self, pref):
        self.preferences = pref

    def cleanup(self):
        self.plot.clear()
        self.draw()

    def showGraph(self, points):
        presUnit = self.preferences.getUnit(PressureUnit.PASCAL)
        rateUnit = self.preferences.getUnit(VelocityUnit.METER_PER_SECOND)
        # I really don't like this, but it is necessary for this graph and the c* output to coexist
        if rateUnit == VelocityUnit.FOOT_PER_SECOND:
            rateUnit = VelocityUnit.INCH_PER_SECOND
        if rateUnit == VelocityUnit.METER_PER_SECOND:
            rateUnit = VelocityUnit.MILLIMETER_PER_SECOND

        self.plot.plot(convertAll(points[0], PressureUnit.PASCAL, presUnit), convertAll(points[1], VelocityUnit.METER_PER_SECOND, rateUnit))
        self.plot.set_xlabel('Pressure - {}'.format(presUnit))
        self.plot.set_ylabel('Burn Rate - {}'.format(rateUnit))
        self.plot.grid(True)
        self.figure.subplots_adjust(top=0.95, bottom=0.25)
        self.draw()
