from math import radians, tan

from PyQt6.QtWidgets import QWidget, QApplication, QGraphicsScene, QGraphicsPolygonItem
from PyQt6.QtGui import QPolygonF, QBrush
from PyQt6.QtCore import QPointF, Qt, QTimer

import motorlib
from ..views.NozzlePreview_ui import Ui_NozzlePreview

class NozzlePreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_NozzlePreview()
        self.ui.setupUi(self)

        self.brush = QBrush()

        if QApplication.instance() and QApplication.instance().isDarkMode():
            self.brush.setColor(Qt.GlobalColor.lightGray)

        self.brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.scene = QGraphicsScene(self)
        self.upper = QGraphicsPolygonItem()
        self.lower = QGraphicsPolygonItem()
        self.upper.setBrush(self.brush)
        self.lower.setBrush(self.brush)
        self.scene.addItem(self.upper)
        self.scene.addItem(self.lower)
        self.ui.tabCrossSection.setScene(self.scene)

        self.ui.tabWidget.currentChanged.connect(self.rescale)

    def loadNozzle(self, nozzle):
        geomAlerts = nozzle.getGeometryErrors()

        self.ui.tabAlerts.clear()
        for err in geomAlerts:
            self.ui.tabAlerts.addItem(err.description)

        self.upper.setPolygon(QPolygonF([]))
        self.lower.setPolygon(QPolygonF([]))

        for alert in geomAlerts:
            if alert.level == motorlib.simResult.SimAlertLevel.ERROR:
                self.ui.tabWidget.setCurrentIndex(0)
                return

        convAngle = radians(nozzle.props['convAngle'].getValue())
        throatLen = nozzle.props['throatLength'].getValue()
        throatRad = nozzle.props['throat'].getValue() / 2
        divAngle = radians(nozzle.props['divAngle'].getValue())
        exitRad = nozzle.props['exit'].getValue() / 2

        # Guess a nozzle outer radius that's a bit bigger than the exit diameter
        outerRad = 1.25 * exitRad

        # If they have a grain diameter, base the nozzle radius on that instead
        if QApplication.instance() and QApplication.instance().fileManager:
            motor = QApplication.instance().fileManager.getCurrentMotor()
            if len(motor.grains) > 0:
                outerRad = motor.grains[0].getProperty('diameter') / 2

        # Casing radius a bit larger than nozzle radius
        casingRad = outerRad * 1.1

        if divAngle != 0:
            divLen = (exitRad - throatRad) / tan(divAngle)
        else:
            divLen = 0
            
        if convAngle != 0:
            convLen = (outerRad - throatRad) / tan(convAngle)
        else:
            convLen = 0

        # We want a bit over a cal of casing sticking off the forward end
        casingLength = (outerRad * 1.25) + convLen + throatLen

        nozzleAftRad = max(exitRad * 1.1, casingRad)
            
        upperPoints = [
            [throatLen, throatRad], # Forward throat point
            [0, throatRad], # Aft throat point
            [-divLen, exitRad], # Exit point
            [-divLen, nozzleAftRad], # Aft-most OD point
            [0, casingRad],
            [casingLength, casingRad], # Casing OD point
            [casingLength, outerRad], # Casing ID point
            [throatLen + convLen, outerRad], # Convergence OD
        ]

        scale = 100 / nozzle.props['exit'].getValue()
        lower = QPolygonF([QPointF(p[0] * scale, p[1] * scale) for p in upperPoints])
        upper = QPolygonF([QPointF(p[0] * scale, -p[1] * scale) for p in upperPoints])

        self.upper.setPolygon(upper)
        self.lower.setPolygon(lower)

        self.ui.tabWidget.setCurrentIndex(1)

        QTimer.singleShot(0, self.rescale) # I really don't know why this "delay" is needed

    def rescale(self):
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.ui.tabCrossSection.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
