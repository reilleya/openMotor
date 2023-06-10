from math import radians, tan

from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsScene, QGraphicsPolygonItem
from PyQt5.QtGui import QPolygonF, QBrush
from PyQt5.QtCore import QPointF, Qt

from motorlib.enums.simAlertLevel import SimAlertLevel
from ..views.NozzlePreview_ui import Ui_NozzlePreview

class NozzlePreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_NozzlePreview()
        self.ui.setupUi(self)

        self.brush = QBrush()
        self.brush.setStyle(1)
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
            if alert.level == SimAlertLevel.ERROR:
                return

        convAngle = radians(nozzle.props['convAngle'].getValue())
        throatLen = nozzle.props['throatLength'].getValue()
        throatRad = nozzle.props['throat'].getValue() / 2
        divAngle = radians(nozzle.props['divAngle'].getValue())
        exitRad = nozzle.props['exit'].getValue() / 2
        outerRad = 1.25 * exitRad
        if QApplication.instance() and QApplication.instance().fileManager: # Check if the app exists and has a fm
            motor = QApplication.instance().fileManager.getCurrentMotor()
            if len(motor.grains) > 0:
                outerRad = motor.grains[0].getProperty('diameter') / 2

        scale = 100 / nozzle.props['exit'].getValue()
        radDiff = exitRad - throatRad
        if divAngle != 0:
            divLen = radDiff / tan(divAngle)
        else:
            divLen = 0
            
        if convAngle != 0:
            convLen = (outerRad - throatRad) / tan(convAngle)
        else:
            convLen = 0
            
        nozzleBottomRad = max(exitRad*1.1, outerRad)
            
        upperPoints = [
            [throatLen, throatRad],
            [0, throatRad],
            [-divLen, exitRad],
            [-divLen, nozzleBottomRad],
            [0, outerRad],
            [throatLen + convLen, outerRad],
        ]
        lower = QPolygonF([QPointF(p[0] * scale, p[1] * scale) for p in upperPoints])
        upper = QPolygonF([QPointF(p[0] * scale, -p[1] * scale) for p in upperPoints])

        self.upper.setPolygon(upper)
        self.lower.setPolygon(lower)
        self.rescale()

    def rescale(self):
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.ui.tabCrossSection.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
