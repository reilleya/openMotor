from itertools import cycle

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GrainPreviewGraph(FigureCanvas):
    def __init__(self):
        super(GrainPreviewGraph, self).__init__(Figure())
        self.setParent(None)
        self.preferences = None

        self.image = None
        self.numContours = 0

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.figure.tight_layout()

        self.plot = self.figure.add_subplot(111)

    def setPreferences(self, pref):
        self.preferences = pref

    def setupImagePlot(self):
        self.figure.subplots_adjust(bottom=0.01, top=0.99, hspace=0)

        self.plot.xaxis.set_visible(False)
        self.plot.yaxis.set_visible(False)
        self.plot.axis('off')

    def setupGraphPlot(self):
        self.plot.set_xticklabels([])
        self.plot.set_yticklabels([])

    def cleanup(self):
        if self.image is not None:
            self.image.remove()
            self.image = None
        if self.numContours > 0:
            for _ in range(0, self.numContours):
                self.plot.lines.pop(0)
            self.numContours = 0
        self.draw()

    def showImage(self, image):
        self.image = self.plot.imshow(image, cmap='Greys')
        self.draw()

    def showContours(self, contours):
        colorCycle = cycle(['r', 'g', 'b', 'y'])
        for contourSet in contours:
            color = next(colorCycle)
            for contour in contourSet:
                self.plot.plot(contour[:, 1], contour[:, 0], linewidth=1, c=color)
                self.numContours += 1
        self.draw()

    def showGraph(self, points):
        self.plot.plot(points[0], points[1], c='b')
        self.numContours += 1
        self.draw()

    def resetGraphBounds(self):
        self.plot.clear()
        self.setupGraphPlot()
