import matplotlib
matplotlib.use('Qt4Agg')

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
        #self.plot.set_ylabel('')
        #self.plot.set_title('Raw data')
    
    def showData(self, simResult):
        self.plot.clear()
        self.setLabels()

        pressureUnit = self.preferences.getUnit('pa')
        forceUnit = self.preferences.getUnit('n')
        self.plot.plot(simResult.time, simResult.kn)
        self.plot.plot(simResult.time, [motorlib.convert(pr, 'pa', pressureUnit) for pr in simResult.pressure])
        self.plot.plot(simResult.time, [motorlib.convert(fr, 'n', forceUnit) for fr in simResult.force])
        self.plot.legend(["KN", "Pressure - " + pressureUnit, "Force - " + forceUnit])
        self.draw()

    def resetPlot(self):
        self.plot.clear()
        self.draw()

    def saveImage(self, filename):
        self.figure.savefig(filename)