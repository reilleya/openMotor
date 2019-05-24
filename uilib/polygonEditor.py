from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtCore import pyqtSignal

import ezdxf
import math
import itertools
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
            path = QFileDialog.getOpenFileName(None, 'Load core geometry', '', 'DXF Files (*.dxf *.DXF)')[0]
        if path != '': # If they cancel the dialog, path will be an empty string
            dwg = ezdxf.readfile(path)
            msp = dwg.modelspace()

            self.points = []
            chunks = []

            for ent in msp:
                if ent.dxftype() == 'ARC':
                    arcPoints = 20
                    part = []
                    sa = ent.dxf.start_angle
                    ea = ent.dxf.end_angle
                    if sa > ea:
                        ea += 360
                    for i in range(0, arcPoints):
                        a = sa + ((ea - sa) * (i / (arcPoints - 1)))
                        px = ent.dxf.center[0] + (math.cos(a * 3.14159 / 180) * ent.dxf.radius)
                        py = ent.dxf.center[1] + (math.sin(a * 3.14159 / 180) * ent.dxf.radius)
                        part.append((px, py))

                    chunks.append(part)

                elif ent.dxftype() == 'CIRCLE':
                    part = []
                    circlePoints = 36
                    for i in range(0, circlePoints):
                        a = 2 * 3.14159 * (i / circlePoints)
                        px = ent.dxf.center[0] + (math.cos(a) * ent.dxf.radius)
                        py = ent.dxf.center[1] + (math.sin(a) * ent.dxf.radius)
                        part.append((px, py))

                    self.points.append(part)

                elif ent.dxftype() == 'LINE':
                    p1 = ent.dxf.end[:2]
                    p2 = ent.dxf.start[:2]

                    chunks.append([p1, p2])

                elif ent.dxftype() == 'LWPOLYLINE':
                    with ent.points() as points:
                        self.points.append(points)

            close = 0.01
            join = None
            while join != []:
                join = []
                for (chunkId, chunk), (compChunkID, compChunk) in itertools.combinations(enumerate(chunks), 2):
                    if motorlib.dist(chunk[0], compChunk[-1]) < close:
                        join = [compChunkID, chunkId, False]
                        break
                    elif motorlib.dist(chunk[-1], compChunk[0]) < close:
                        join = [chunkId, compChunkID, False]
                        break
                    elif motorlib.dist(chunk[-1], compChunk[-1]) < close:
                        join = [chunkId, compChunkID, True]
                        break
                    elif motorlib.dist(chunk[0], compChunk[0]) < close:
                        join = [chunkId, compChunkID, True]
                        break
                if join != []:
                    addChunk = chunks[join[1]]
                    if join[2]:
                        addChunk.reverse()
                    chunks[join[0]] += addChunk
                    del chunks[join[1]]
            self.points += chunks

            self.pointsChanged.emit()
