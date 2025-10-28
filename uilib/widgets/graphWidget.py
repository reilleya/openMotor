from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.axisartist import SubplotHost
from mpl_toolkits.axes_grid1.parasite_axes import ParasiteAxes

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
        self.figure.clear()
        self.plot = SubplotHost(self.figure, 111)
        self.figure.add_subplot(self.plot)
        self.figure.tight_layout()

        xAxisUnit = self.preferences.getUnit(simResult.channels[xChannel].unit)

        legend = []

        if simResult.channels[xChannel].valueType in (list, tuple):
            if len(grains) > 0:
                xData = selectGrains(simResult.channels[xChannel].getData(xAxisUnit), grains)
            else:
                return
        else:
            xData = simResult.channels[xChannel].getData(xAxisUnit)

        for channelNum, channelName in enumerate(yChannels):
            plotter = self.plot
            if self.preferences.getDict()['general']['dualAxis'] and len(yChannels) == 2 and channelNum == 1:
                self.figure.subplots_adjust(right=0.9, left=0.1)
                plotter = ParasiteAxes(self.plot, sharex=self.plot)
                self.plot.parasites.append(plotter)
                plotter.axis['right'].set_visible(True)
                plotter.axis['left'].set_visible(False)
                self.figure.add_axes(plotter)

            channel = simResult.channels[channelName]
            yUnit = self.preferences.getUnit(channel.unit)
            if channel.valueType in (list, tuple) and len(grains) > 0:
                yData = selectGrains(channel.getData(yUnit), grains)
                plotter.plot(xData, yData)
            elif channel.valueType in (int, float):
                plotter.plot(xData, channel.getData(yUnit))
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
            
            if self.preferences.getDict()['general']['dualAxis'] and len(yChannels) == 2:
                plotter2 = self.plot if channelNum == 0 else plotter
                if yUnit != '':
                    plotter2.set_ylabel('{} - {}'.format(channel.name, yUnit))
                else:
                    plotter2.set_ylabel(channel.name)

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
