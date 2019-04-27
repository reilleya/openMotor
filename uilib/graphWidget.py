import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import motorlib

class graphWidget(FigureCanvas):
    def __init__(self, parent):
        super(graphWidget, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.setLabels()
        self.preferences = None

    def setPreferences(self, pref):
        self.preferences = pref

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot = self.figure.add_subplot(111)
        self.figure.tight_layout()

    def setLabels(self):
        self.plot.set_xlabel('Time (s)')

    def showData(self, simResult):
        self.plot.clear()
        self.setLabels()

        pressureUnit = self.preferences.getUnit('Pa')
        forceUnit = self.preferences.getUnit('N')
        self.plot.plot(simResult.channels['time'].getData(), simResult.channels['kn'].getData())
        self.plot.plot(simResult.channels['time'].getData(), simResult.channels['pressure'].getData(pressureUnit))
        self.plot.plot(simResult.channels['time'].getData(), simResult.channels['force'].getData(forceUnit))
        self.plot.legend(["Kn", "Pressure - " + pressureUnit, "Force - " + forceUnit])
        self.draw()

    def resetPlot(self):
        self.plot.clear()
        self.draw()

    def saveImage(self, filename):
        self.figure.savefig(filename)
