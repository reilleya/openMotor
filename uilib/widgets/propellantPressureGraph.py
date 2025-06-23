from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from motorlib.units import convertAll

class PropellantPressureGraph(FigureCanvas):
    def __init__(self):
        super(PropellantPressureGraph, self).__init__(Figure())
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

        self.plot.plot(points[0], convertAll(points[1], 'Pa', presUnit))
        self.plot.set_xlabel('Kn')
        self.plot.set_ylabel('Pressure - {}'.format(presUnit))
        self.plot.grid(True)
        self.figure.subplots_adjust(top=0.95, bottom=0.25)
        self.draw()
