from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def selectGrains(data, grains):
    # Returns the data corresponding to specific grains from data structured like [[G1, G2], [G1, G2], [G1, G2]...]
    out = []
    for frame in data:
        out.append([])
        for grain in grains:
            out[-1].append(frame[grain])
    return out

class GraphWidget(FigureCanvas):
    def __init__(self, parent):
        super(GraphWidget, self).__init__(Figure())
        self.setParent(None)
        self.setupPlot()
        self.preferences = None

    def setPreferences(self, pref):
        self.preferences = pref

    def setupPlot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot = self.figure.add_subplot(111)
        self.figure.tight_layout()

    def plotData(self, simResult, xChannel, yChannels, grains):
        self.plot.clear()

        xAxisUnit = self.preferences.getUnit(simResult.channels[xChannel].unit)

        legend = []

        if simResult.channels[xChannel].valueType in (list, tuple):
            if len(grains) > 0:
                xData = selectGrains(simResult.channels[xChannel].getData(xAxisUnit), grains)
            else:
                return
        else:
            xData = simResult.channels[xChannel].getData(xAxisUnit)

        for channelName in yChannels:
            channel = simResult.channels[channelName]
            yUnit = self.preferences.getUnit(channel.unit)
            if channel.valueType in (list, tuple) and len(grains) > 0:
                yData = selectGrains(channel.getData(yUnit), grains)
                self.plot.plot(xData, yData)
            elif channel.valueType in (int, float):
                self.plot.plot(xData, channel.getData(yUnit))
            if channel.valueType in (int, float):
                if yUnit != '':
                    legend.append('{} - {}'.format(channel.name, yUnit))
                else:
                    legend.append(channel.name)
            elif channel.valueType in (list, tuple):
                for i in range(len(channel.getData()[0])):
                    if i in grains:
                        if yUnit != '':
                            legend.append('{} - Grain {} - {}'.format(channel.name, i + 1, yUnit))
                        else:
                            legend.append('{} - Grain {}'.format(channel.name, i + 1))
        self.plot.legend(legend)
        self.plot.set_xlabel('{} - {}'.format(simResult.channels[xChannel].name, xAxisUnit))
        self.plot.grid(True)

    def saveImage(self, simResult, xChannel, yChannels, grains, path):
        self.plotData(simResult, xChannel, yChannels, grains)
        self.plot.set_title(simResult.getFullDesignation())
        self.figure.savefig(path, bbox_inches="tight")
        # Clear, but don't draw to not wipe away the graph in the UI
        self.plot.clear()

    def showData(self, simResult, xChannel, yChannels, grains):
        self.plotData(simResult, xChannel, yChannels, grains)
        self.draw()

    def resetPlot(self):
        self.plot.clear()
        self.draw()
