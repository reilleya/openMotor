from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from itertools import cycle


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
