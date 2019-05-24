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

            self.points = [[]]

            for ent in msp:
                if ent.dxftype() == 'ARC':
                    print('ARC:')
                    arcPoints = 20
                    part = []
                    sa = ent.dxf.start_angle
                    ea = ent.dxf.end_angle
                    print(sa)
                    print(ea)
                    print()

                    if sa > ea:
                        ea += 360
                    for i in range(0, arcPoints):
                        a = sa + ((ea - sa) * (i / (arcPoints - 1)))
                        px = ent.dxf.center[0] + (math.cos(a * 3.14159 / 180) * ent.dxf.radius)
                        py = ent.dxf.center[1] + (math.sin(a * 3.14159 / 180) * ent.dxf.radius)
                        part.append((px, py))

                    print('Goal: ' + str(self.points[-1][-1]))
                    print('Start: ' + str(part[0]))
                    print('End: ' + str(part[-1]))

                    sDist = motorlib.dist(part[0], self.points[-1][-1])
                    eDist = motorlib.dist(part[-1], self.points[-1][-1])
                    print(sDist)
                    print(eDist)

                    if eDist < sDist:
                        part.reverse()

                    self.points[-1] += part
                    print('----------------------------')

                elif ent.dxftype() == 'LINE':
                    print('LINE: ')
                    lStart = ent.dxf.end[:2]
                    lEnd = ent.dxf.start[:2]
                    if len(self.points[-1]) > 0 and motorlib.dist(lStart, self.points[-1][-1]) > 0.1:
                        self.points.append([])

                    if len(self.points[-1]) > 0:
                        print('Goal: ' + str(self.points[-1][-1]))
                    print('Start: ' + str(lStart))
                    print('End: ' + str(lEnd))

                    self.points[-1].append(lStart)
                    self.points[-1].append(lEnd)
                    print('***************************')

                elif ent.dxftype() == 'LWPOLYLINE':
                    with lwpl.points() as points:
                        self.points.append(points)
                    self.points.append([])

            self.pointsChanged.emit()

# Todo: Circle/ellipse, core sep, props to set core position, comments
