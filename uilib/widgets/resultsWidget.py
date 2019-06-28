from threading import Thread

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QHeaderView
from PyQt5.QtCore import pyqtSignal

from .grainImageWidget import GrainImageWidget

from ..views.ResultsWidget_ui import Ui_ResultsWidget

class ResultsWidget(QWidget):
    imageReady = pyqtSignal(tuple)

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)

        self.ui.channelSelectorX.setupChecks(False, default='time', exclude=['mass', 'massFlow', 'massFlux'])
        self.ui.channelSelectorX.setTitle('X Axis')
        self.ui.channelSelectorY.setupChecks(True, default=['kn', 'pressure', 'force'])
        self.ui.channelSelectorY.setTitle('Y Axis')
        self.ui.channelSelectorX.checksChanged.connect(self.drawGraphs)
        self.ui.channelSelectorY.checksChanged.connect(self.drawGraphs)
        self.ui.grainSelector.checksChanged.connect(self.drawGraphs)

        self.preferences = None
        self.simResult = None

        self.ui.horizontalSliderTime.valueChanged.connect(self.updateGrainImages)
        self.imageReady.connect(self.displayImage)
        self.ui.tableWidgetGrains.setRowHeight(0, 128)
        self.grainImageWidgets = []
        self.grainImages = []

    def setPreferences(self, pref):
        self.preferences = pref
        self.ui.widgetGraph.setPreferences(pref)

    def showData(self, simResult):
        self.simResult = simResult
        self.ui.grainSelector.resetChecks()
        self.ui.grainSelector.setupChecks(simResult, True)
        self.drawGraphs()

        self.ui.horizontalSliderTime.setMaximum(len(simResult.channels['time'].getData()) - 1)
        self.ui.tableWidgetGrains.setColumnCount(len(simResult.motor.grains))
        for _ in range(len(self.grainImageWidgets)):
            del self.grainImageWidgets[-1]
        for gid, grain in enumerate(simResult.motor.grains):
            self.grainImageWidgets.append(GrainImageWidget())
            #self.grainImageWidgets[-1].setupImagePlot()
            self.ui.tableWidgetGrains.setCellWidget(0, gid, self.grainImageWidgets[-1])
            self.grainImages.append(grain.getRegressionData(128, coreBlack=False)[1])
            self.ui.tableWidgetGrains.horizontalHeader().setSectionResizeMode(gid, QHeaderView.ResizeToContents)
        self.updateGrainImages()
        self.ui.tableWidgetGrains.setColumnWidth(0, 128)

    def drawGraphs(self):
        if self.simResult is not None:
            xCheck = self.ui.channelSelectorX.getSelectedChannels()[0]
            yChecks = self.ui.channelSelectorY.getSelectedChannels()
            grains = self.ui.grainSelector.getSelectedGrains()
            self.ui.widgetGraph.showData(self.simResult, xCheck, yChecks, grains)

    def updateGrainImages(self):
        if self.simResult is not None:
            for gid, grain in enumerate(self.simResult.motor.grains):
                regDist = self.simResult.channels['regression'].getPoint(self.ui.horizontalSliderTime.value())[gid]
                dataThread = Thread(target=self._genData, args=[grain, gid, regDist])
                dataThread.start()

    def _genData(self, grain, gid, regDist):
        #mapDist = grain.normalize(regDist)
        mapDist = regDist / (0.5 * grain.props['diameter'].getValue())
        image = self.grainImages[gid] > mapDist
        self.imageReady.emit((image, gid))

    def displayImage(self, inp):
        image, gid = inp
        self.grainImageWidgets[gid].showImage(image)

    def resetPlot(self):
        self.ui.grainSelector.resetChecks()
        self.ui.widgetGraph.resetPlot()
