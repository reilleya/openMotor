from threading import Thread

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

import motorlib

from ..views.GrainPreview_ui import Ui_GrainPreview

class GrainPreviewWidget(QWidget):

    previewReady = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.ui = Ui_GrainPreview()
        self.ui.setupUi(self)

        self.ui.tabFace.setupImagePlot()
        self.ui.tabRegression.setupImagePlot()
        self.ui.tabAreaGraph.setupGraphPlot()

        # Used to navigate back to the tab the user was on after they clear alerts
        self.lastNonAlertTab = 1

        self.ui.tabWidget.currentChanged.connect(self.onTabChanged)

        self.previewReady.connect(self.updateView)

    def loadGrain(self, grain):
        geomAlerts = grain.getGeometryErrors()

        self.ui.tabAlerts.clear()
        for err in geomAlerts:
            self.ui.tabAlerts.addItem(err.description)

        for alert in geomAlerts:
            if alert.level == motorlib.simResult.SimAlertLevel.ERROR:
                # Go to alerts tab and clear up graph/images
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.tabFace.cleanup()
                self.ui.tabRegression.cleanup()
                self.ui.tabAreaGraph.cleanup()
                return

        # If they were on the alert tab, go to their last image/graph tab. Otherwise, let them stay
        if self.ui.tabWidget.currentIndex() == 0:
            self.ui.tabWidget.setCurrentIndex(self.lastNonAlertTab)

        # Generate the contents to show on the image/graph tabs
        dataThread = Thread(target=self._genData, args=[grain])
        dataThread.start()

    def _genData(self, grain):
        out = grain.getRegressionData(250, coreBlack=False)
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

    def onTabChanged(self, tabIndex):
        if tabIndex != 0:
            self.lastNonAlertTab = tabIndex

    def cleanup(self):
        self.lastNonAlertTab = 1
        self.ui.tabAlerts.clear()
        self.ui.tabRegression.cleanup()
        self.ui.tabFace.cleanup()
        self.ui.tabAreaGraph.cleanup()
        self.ui.tabAreaGraph.resetGraphBounds()
