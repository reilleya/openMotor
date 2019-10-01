from PyQt5.QtWidgets import QDialog

from motorlib.simResult import singleValueChannels, multiValueChannels
from ..converter import Exporter

from ..views.ImageExporter_ui import Ui_ImageExporter

class ImageExportMenu(QDialog):
    def __init__(self, converter):
        QDialog.__init__(self)
        self.ui = Ui_ImageExporter()
        self.ui.setupUi(self)
        self.converter = converter

    def exec(self):
        self.ui.independent.resetChecks()
        self.ui.independent.setupChecks(False, exclude=['kn', 'pressure', 'force', 'mass',
                                                        'massFlow', 'massFlux', 'exitPressure', 'dThroat'])
        self.ui.independent.checksChanged.connect(self.validateChecks)
        self.ui.dependent.resetChecks()
        self.ui.dependent.setupChecks(True)
        self.ui.grainSelector.resetChecks()
        self.ui.grainSelector.setupChecks(self.converter.manager.simRes, True)
        if super().exec():
            xChannel = self.ui.independent.getSelectedChannels()[0]
            yChannels = self.ui.dependent.getSelectedChannels()
            grains = self.ui.grainSelector.getSelectedGrains()
            return [xChannel, yChannels, grains]
        return None

    def validateChecks(self):
        if self.ui.independent.getSelectedChannels()[0] in multiValueChannels:
            self.ui.dependent.unselect(singleValueChannels)
            self.ui.dependent.toggleEnabled(singleValueChannels, False)
        else:
            self.ui.dependent.toggleEnabled(singleValueChannels, True)


class ImageExporter(Exporter):
    def __init__(self, manager):
        super().__init__(manager, 'Image File',
                         'Exports the results of a simulation in a graph.', {'.png': 'Portable network graphic'})
        self.menu = ImageExportMenu(self)
        self.reqNotMet = "Must have run a simulation to export a .PNG file."

    def doConversion(self, path, config):
        # TODO: This is ugly and should be refactored. The app should own the grapher.
        graphWidget = self.manager.app.window.ui.resultsWidget.ui.widgetGraph
        graphWidget.saveImage(self.manager.simRes, config[0], config[1], config[2], path)

    def checkRequirements(self):
        return self.manager.simRes is not None
