from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from itertools import cycle
from threading import Thread

import motorlib


class grainPreviewGraph(FigureCanvas):
    def __init__(self):
        super(grainPreviewGraph, self).__init__(Figure())
        self.setParent(None)
        self.preferences = None

        self.im = None
        self.numContours = 0

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.tight_layout()

        self.plot = self.figure.add_subplot(111)

    def setPreferences(self, pref):
        self.preferences = pref

    def setupImagePlot(self):
        self.figure.subplots_adjust(bottom = 0.01, top = 0.99, hspace = 0)

        self.plot.xaxis.set_visible(False)
        self.plot.yaxis.set_visible(False)
        self.plot.axis('off')

    def setupGraphPlot(self):
        self.plot.set_xticklabels([])
        self.plot.set_yticklabels([])

    def cleanup(self):
        if self.im is not None:
            self.im.remove()
            self.im = None
        if self.numContours > 0:
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
        self.plot.plot(points[0], points[1], c = 'b')
        self.numContours += 1
        self.draw()

    def resetGraphBounds(self):
        self.plot.clear()
        self.setupGraphPlot()


class grainPreviewWidget(QWidget):

    previewReady = pyqtSignal(tuple)

    def __init__(self):
        # TODO: this "hack" is to avoid circular imports.
        from .views.GrainPreview_ui import Ui_GrainPreview

        super().__init__()
        self.ui = Ui_GrainPreview()
        self.ui.setupUi(self)

        self.ui.tabFace.setupImagePlot()
        self.ui.tabRegression.setupImagePlot()
        self.ui.tabAreaGraph.setupGraphPlot()

        self.previewReady.connect(self.updateView)

    def loadGrain(self, grain):
        geomAlerts = grain.getGeometryErrors()
        for alert in geomAlerts:
            if alert.level == motorlib.simAlertLevel.ERROR:
                return

        dataThread = Thread(target = self._genData, args = [grain])
        dataThread.start()

    def _genData(self, grain):
        out = grain.getRegressionData(250)
        self.previewReady.emit(out)

    def updateView(self, data):
        coreIm, regImage, contours, contourLengths = data

        self.ui.tabFace.cleanup()
        self.ui.tabFace.showImage(coreIm)

        if regImage is not None:
            self.ui.tabRegression.cleanup()
            self.ui.tabRegression.showImage(regImage)
            self.ui.tabRegression.showContours(contours)

            points = [[], []]

            for k in contourLengths.keys():
                points[0].append(k)
                points[1].append(contourLengths[k])

            self.ui.tabAreaGraph.cleanup()
            self.ui.tabAreaGraph.showGraph(points)

    def cleanup(self):
        self.ui.tabRegression.cleanup()
        self.ui.tabFace.cleanup()
        self.ui.tabAreaGraph.cleanup()
        self.ui.tabAreaGraph.resetGraphBounds()
