from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        presUnit = self.preferences.getUnit('Pa')
        rateUnit = self.preferences.getUnit('m/s')
        # I really don't like this, but it is necessary for this graph and the c* output to coexist
        if rateUnit == 'ft/s':
            rateUnit = 'in/s'
        if rateUnit == 'm/s':
            rateUnit = 'mm/s'

        self.plot.plot(convertAll(points[0], 'Pa', presUnit), convertAll(points[1], 'm/s', rateUnit))
        self.plot.set_xlabel('Pressure - ' + presUnit)
        self.plot.set_ylabel('Burn Rate - ' + rateUnit)
        self.plot.grid(True)
        self.figure.subplots_adjust(top=0.95, bottom=0.15)
        self.draw()
