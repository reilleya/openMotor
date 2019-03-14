from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from itertools import cycle

import motorlib

class grainPreviewGraph(FigureCanvas):
    def __init__(self):
        super(grainPreviewGraph, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.preferences = None

        self.im = None
        self.numContours = 0

    def setPreferences(self, pref):
        self.preferences = pref

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.tight_layout()

        self.figure.subplots_adjust(bottom = 0.01, top = 0.99, hspace = 0)

        self.plot = self.figure.add_subplot(111)
        self.plot.xaxis.set_visible(False)
        self.plot.yaxis.set_visible(False)
        self.plot.axis('off')

    def cleanup(self):
        if self.im is not None:
            self.im.remove()
            self.im = None
            for i in range(0, self.numContours):
                self.plot.lines.pop(0)
            self.numContours = 0
            self.draw()

    def showImage(self, image):
        self.im = self.plot.imshow(image, cmap = 'Greys')
        self.draw()

    def showContours(self, contours):
        color_cycle = cycle(['r', 'g', 'b', 'y'])
        for contourSet in contours:
            c = next(color_cycle)
            for contour in contourSet:
                self.plot.plot(contour[:, 1], contour[:, 0], linewidth = 1, c = c)
                self.numContours += 1
        self.draw()

    def showGraph(self, points):
        self.plot.plot(points[0], points[1])

class grainPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("resources/GrainPreview.ui", self)

    def loadGrain(self, grain):

        if grain.props['diameter'].getValue() == 0: # Todo: replace with more rigorous geometry checks
            return

        coreIm, regImage, contours, contourLengths = grain.getRegressionData(200)

        self.tabFace.cleanup()
        self.tabFace.showImage(coreIm)

        if regImage is not None:
            self.tabRegression.cleanup()
            self.tabRegression.showImage(regImage)
            self.tabRegression.showContours(contours)

    def cleanup(self):
        self.tabRegression.cleanup()
        self.tabFace.cleanup()
