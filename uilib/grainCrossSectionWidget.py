import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import motorlib

class grainCrossSectionWidget(FigureCanvas):
    def __init__(self):
        super(grainCrossSectionWidget, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.preferences = None

        self.im = None

    def setPreferences(self, pref):
        self.preferences = pref

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.tight_layout()

        self.plot = self.figure.add_subplot(111)
        self.plot.xaxis.set_visible(False)
        self.plot.yaxis.set_visible(False)
        self.plot.axis('off')

    def showGrain(self, grain):
        if self.im is not None:
            self.im.remove()

        self.im = self.plot.imshow(grain.getPreview(300), cmap = 'Greys')

        self.draw()
