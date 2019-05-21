from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtCore import pyqtSignal

import ezdxf
import math
import motorlib

class PolygonEditor(QWidget):

    pointsChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())

        self.selectButton = QPushButton('Select')
        self.selectButton.pressed.connect(self.loadDXF)
        self.layout().addWidget(self.selectButton)

        self.points = []

        self.preferences = None

    def loadDXF(self, path = None):
        if path is None:
            path = QFileDialog.getOpenFileName(None, 'Load core geometry', '', 'DXF Files (*.dxf)')[0]
        if path != '': # If they cancel the dialog, path will be an empty string
            dwg = ezdxf.readfile(path)
            msp = dwg.modelspace()

            self.points = []

            if self.preferences is None:
                inUnit = 'in'
            else:
                inUnit = self.preferences.getUnit('m')

            for lwpl in msp.query('LWPOLYLINE'):
                with lwpl.points() as points:
                    self.points.append([(motorlib.convert(p[0], inUnit, 'm'), motorlib.convert(p[1], inUnit, 'm')) for p in points])

            p = []

            for ent in msp:
                if ent.dxftype() == 'ARC':
                    part = []
                    sa = ent.dxf.start_angle
                    ea = ent.dxf.end_angle
                    if sa > ea:
                        ea += 360
                    for i in range(0, 10):
                        a = sa + ((ea - sa) * (i / 9))
                        px = ent.dxf.center[0] + (math.cos(a * 3.14159 / 180) * ent.dxf.radius)
                        py = ent.dxf.center[1] + (math.sin(a * 3.14159 / 180) * ent.dxf.radius)
                        part.append((motorlib.convert(px, inUnit, 'm'), motorlib.convert(py, inUnit, 'm')))
                    if motorlib.dist(part[-1], p[-1]) < motorlib.dist(part[0], p[-1]):
                        part.reverse()
                    p += part

                if ent.dxftype() == 'LINE':
                    p.append((motorlib.convert(ent.dxf.end[0], inUnit, 'm'), motorlib.convert(ent.dxf.end[1], inUnit, 'm')))
                    p.append((motorlib.convert(ent.dxf.start[0], inUnit, 'm'), motorlib.convert(ent.dxf.start[1], inUnit, 'm')))

            self.points.append(p)

            self.pointsChanged.emit()
