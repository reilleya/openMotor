from PyQt5.QtWidgets import QWidget, QHeaderView, QLabel
import numpy as np

import motorlib
from motorlib.enums.multiValueChannels import MultiValueChannels
from motorlib.enums.singleValueChannels import SingleValueChannels

from .grainImageWidget import GrainImageWidget

from ..views.ResultsWidget_ui import Ui_ResultsWidget

class ResultsWidget(QWidget):
    # These channels are extracted from the simResult amd put into the grain table in this order that should match
    # the labels in the .ui file
    grainTableFields = (MultiValueChannels.MASS,
                        MultiValueChannels.MASS_FLOW,
                        MultiValueChannels.MASS_FLUX,
                        MultiValueChannels.WEB)

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_ResultsWidget()
        self.ui.setupUi(self)
        self.preferences = None
        self.simResult = None
        self.cachedChecks = None

        excludes = [SingleValueChannels.KN,
                    SingleValueChannels.PRESSURE,
                    SingleValueChannels.FORCE,
                    MultiValueChannels.MASS,
                    MultiValueChannels.MASS_FLOW,
                    MultiValueChannels.MASS_FLUX,
                    SingleValueChannels.EXIT_PRESSURE,
                    SingleValueChannels.D_THROAT,
                    SingleValueChannels.VOLUME_LOADING]
        self.ui.channelSelectorX.setupChecks(False, default=SingleValueChannels.TIME, exclude=excludes)
        self.ui.channelSelectorX.setTitle('X Axis')
        self.ui.channelSelectorY.setupChecks(True,
                                             default=[SingleValueChannels.KN,
                                                      SingleValueChannels.PRESSURE,
                                                      SingleValueChannels.FORCE],
                                             exclude=[SingleValueChannels.TIME])
        self.ui.channelSelectorY.setTitle('Y Axis')
        self.ui.channelSelectorX.checksChanged.connect(self.xSelectionChanged)
        self.ui.channelSelectorY.checksChanged.connect(self.drawGraphs)
        self.ui.grainSelector.checksChanged.connect(self.drawGraphs)

        self.ui.horizontalSliderTime.valueChanged.connect(self.updateGrainTab)
        self.ui.tableWidgetGrains.setRowHeight(0, 128)
        self.grainImageWidgets = []
        self.grainImages = []
        self.grainLabels = []

    def setPreferences(self, pref):
        self.preferences = pref
        self.ui.widgetGraph.setPreferences(pref)

    def showData(self, simResult):
        if self.simResult is not None:
            newMotor = len(simResult.motor.grains) != len(self.simResult.motor.grains)
        else:
            newMotor = True
        self.simResult = simResult
        self.ui.grainSelector.resetChecks()
        self.ui.grainSelector.setupChecks(simResult, True)
        if not newMotor and self.cachedChecks is not None:
            self.ui.grainSelector.setChecks(self.cachedChecks)
        self.drawGraphs()

        self.cleanupGrainTab()
        self.ui.horizontalSliderTime.setMaximum(len(simResult.channels[SingleValueChannels.TIME].getData()) - 1)
        self.ui.tableWidgetGrains.setColumnCount(len(simResult.motor.grains))
        for _ in range(len(self.grainImageWidgets)):
            del self.grainImageWidgets[-1]
        for gid, grain in enumerate(simResult.motor.grains):
            self.grainImageWidgets.append(GrainImageWidget())
            self.grainLabels.append({})
            self.ui.tableWidgetGrains.setCellWidget(0, gid, self.grainImageWidgets[-1])
            if isinstance(grain, motorlib.grain.PerforatedGrain):
                self.grainImages.append(grain.getRegressionData(128, coreBlack=False)[1])
            else:
                self.grainImages.append(None)
            for fid, field in enumerate(self.grainTableFields):
                self.grainLabels[gid][field] = QLabel(field)
                self.ui.tableWidgetGrains.setCellWidget(1 + fid, gid, self.grainLabels[gid][field])
        self.updateGrainTab()

    def xSelectionChanged(self):
        if self.ui.channelSelectorX.getSelectedChannels()[0] in MultiValueChannels:
            self.ui.channelSelectorY.unselect(SingleValueChannels)
            self.ui.channelSelectorY.toggleEnabled(SingleValueChannels, False)
        else:
            self.ui.channelSelectorY.toggleEnabled(SingleValueChannels, True)
        self.drawGraphs()

    def drawGraphs(self):
        if self.simResult is None:
            return
        xCheck = self.ui.channelSelectorX.getSelectedChannels()[0]
        yChecks = self.ui.channelSelectorY.getSelectedChannels()
        grains = self.ui.grainSelector.getSelectedGrains()
        self.ui.widgetGraph.showData(self.simResult, xCheck, yChecks, grains)

    def updateGrainTab(self):
        if self.simResult is not None:
            index = self.ui.horizontalSliderTime.value()
            for gid, grain in enumerate(self.simResult.motor.grains):
                if self.grainImages[gid] is not None:
                    regDist = self.simResult.channels[MultiValueChannels.REGRESSION].getPoint(index)[gid]
                    webRemaining = self.simResult.channels[MultiValueChannels.WEB].getPoint(index)[gid]
                    hasWebLeft = webRemaining > self.simResult.motor.config.getProperty('burnoutWebThres')
                    mapDist = regDist / (0.5 * grain.props['diameter'].getValue())
                    image = np.logical_and(self.grainImages[gid] > mapDist, hasWebLeft)
                    self.grainImageWidgets[gid].showImage(image)
                else:
                    self.grainImageWidgets[gid].setText('-')
                self.ui.tableWidgetGrains.horizontalHeader().setSectionResizeMode(gid, QHeaderView.ResizeToContents)
                for field in self.grainTableFields:
                    fromUnit = self.simResult.channels[field].unit
                    toUnit = self.preferences.getUnit(fromUnit)
                    val = motorlib.units.convert(self.simResult.channels[field].getPoint(index)[gid], fromUnit, toUnit)
                    self.grainLabels[gid][field].setText('{:.3f} {}'.format(val, toUnit))

            currentTime = self.simResult.channels[SingleValueChannels.TIME].getPoint(index)
            remainingTime = self.simResult.channels[SingleValueChannels.TIME].getLast() - currentTime
            self.ui.labelTimeProgress.setText('{:.3f} s'.format(currentTime))
            self.ui.labelTimeRemaining.setText('{:.3f} s'.format(remainingTime))

            currentImpulse = self.simResult.getImpulse(index)
            remainingImpulse = self.simResult.getImpulse() - currentImpulse
            impUnit = self.preferences.getUnit('Ns')
            self.ui.labelImpulseProgress.setText(motorlib.units.convFormat(currentImpulse, 'Ns', impUnit))
            self.ui.labelImpulseRemaining.setText(motorlib.units.convFormat(remainingImpulse, 'Ns', impUnit))

            currentMass = self.simResult.getPropellantMass(index)
            remainingMass = self.simResult.getPropellantMass() - currentMass
            massUnit = self.preferences.getUnit('kg')
            self.ui.labelMassProgress.setText(motorlib.units.convFormat(remainingMass, 'kg', massUnit))
            self.ui.labelMassRemaining.setText(motorlib.units.convFormat(currentMass, 'kg', massUnit))

            currentISP = self.simResult.getISP(index)
            self.ui.labelISPProgress.setText('{:.3f} s'.format(currentISP))
            if currentMass != 0:
                remainingISP = remainingImpulse / (currentMass * 9.80665)
                self.ui.labelISPRemaining.setText('{:.3f} s'.format(remainingISP))
            else:
                self.ui.labelISPRemaining.setText('-')

    def resetPlot(self):
        self.cachedChecks = self.ui.grainSelector.getSelectedGrains()
        self.ui.grainSelector.resetChecks()
        self.ui.widgetGraph.resetPlot()
        self.cleanupGrainTab()

    def cleanupGrainTab(self):
        self.ui.horizontalSliderTime.setValue(0)
        for _ in range(len(self.grainImageWidgets)):
            del self.grainImageWidgets[-1]
            del self.grainImages[-1]
        self.ui.tableWidgetGrains.setColumnCount(0)
        self.ui.labelTimeProgress.setText('-')
        self.ui.labelTimeRemaining.setText('-')
        self.ui.labelImpulseProgress.setText('-')
        self.ui.labelImpulseRemaining.setText('-')
        self.ui.labelMassProgress.setText('-')
        self.ui.labelMassRemaining.setText('-')
        self.ui.labelISPProgress.setText('-')
        self.ui.labelISPRemaining.setText('-')
