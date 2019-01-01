import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class graphWidget(FigureCanvas):
    def __init__(self, parent):
        super(graphWidget, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.setLabels()

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot = self.figure.add_subplot(111)

    def setLabels(self):
        self.plot.set_xlabel('Time (s)')
        #self.plot.set_ylabel('')
        #self.plot.set_title('Raw data')
    
    def showData(self, time, data):
        self.plot.clear()
        self.setLabels()
        for d in data:
            self.plot.plot(time, d)
        self.plot.legend(["KN", "Pressure"])
        self.draw()

    def saveImage(self, filename):
        self.figure.savefig(filename)