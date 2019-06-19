from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget

from ..views.ResultsWidget_ui import Ui_ResultsWidget

class ResultsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)

        self.ui.channelSelectorX.setupChecks(False, default='time', exclude=['mass', 'massFlow', 'massFlux'])
        self.ui.channelSelectorY.setupChecks(True, default=['kn', 'pressure', 'force'])
        self.ui.channelSelectorX.checksChanged.connect(self.display)
        self.ui.channelSelectorY.checksChanged.connect(self.display)

        self.preferences = None
        self.simResult = None

    def setPreferences(self, pref):
        self.preferences = pref
        self.ui.widgetGraph.setPreferences(pref)

    def showData(self, simResult):
        self.simResult = simResult
        self.display()

    def display(self):
        if self.simResult is not None:
            xCheck = self.ui.channelSelectorX.getSelectedChannels()[0]
            yChecks = self.ui.channelSelectorY.getSelectedChannels()
            self.ui.widgetGraph.showData(self.simResult, xCheck, yChecks)

    def resetPlot(self):
        pass
