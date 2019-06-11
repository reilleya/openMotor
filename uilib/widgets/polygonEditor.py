import math
import itertools

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFileDialog, QApplication
from PyQt5.QtCore import pyqtSignal

import ezdxf
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

    def loadDXF(self, path=None):
        if path is None:
            path = QFileDialog.getOpenFileName(None, 'Load core geometry', '', 'DXF Files (*.dxf *.DXF)')[0]
        if path != '': # If they cancel the dialog, path will be an empty string
            dwg = ezdxf.readfile(path)
            msp = dwg.modelspace()

            alerts = []
            self.points = [] # Closed contours go here
            chunks = [] # Individual segments of lines or arcs go here

            for ent in msp:
                if ent.dxftype() == 'ARC':
                    arcPoints = 20 # Number of segments in the arc
                    part = []
                    startAngle = ent.dxf.start_angle
                    endAngle = ent.dxf.end_angle
                    if startAngle > endAngle: # This ensures that the angle step (ea - sa) is not negative
                        endAngle += 360
                    for i in range(0, arcPoints):
                        angle = startAngle + ((endAngle - startAngle) * (i / (arcPoints - 1)))
                        pointX = ent.dxf.center[0] + (math.cos(angle * math.pi / 180) * ent.dxf.radius)
                        pointY = ent.dxf.center[1] + (math.sin(angle * math.pi / 180) * ent.dxf.radius)
                        part.append((pointX, pointY))

                    chunks.append(part)

                elif ent.dxftype() == 'CIRCLE':
                    part = []
                    circlePoints = 36 # Number of segments in the arc
                    for i in range(0, circlePoints):
                        angle = 2 * math.pi * (i / circlePoints)
                        pointX = ent.dxf.center[0] + (math.cos(angle) * ent.dxf.radius)
                        pointY = ent.dxf.center[1] + (math.sin(angle) * ent.dxf.radius)
                        part.append((pointX, pointY))

                    self.points.append(part)

                elif ent.dxftype() == 'LINE':
                    point1 = ent.dxf.end[:2]
                    point2 = ent.dxf.start[:2]

                    chunks.append([point1, point2])

                elif ent.dxftype() == 'LWPOLYLINE':
                    with ent.points() as points:
                        self.points.append(points)

                else:
                    alerts.append("Can't import entity of type: " + ent.dxftype())

            # Join together the segments in chunks to closed contours
            close = 0.001 # Max distance between endpoints of adjacent segments
            join = None
            while join != []:
                join = [] # Will be populated like [ida, idb, flip] if there is work to do
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
                if join != []: # Add the second chunk on to the first and flip it if the bool is true
                    addChunk = chunks[join[1]]
                    if join[2]:
                        addChunk.reverse()
                    chunks[join[0]] += addChunk
                    del chunks[join[1]]

            oldLen = len(chunks)
            chunks = list(filter(lambda chunk: motorlib.dist(chunk[0], chunk[-1]) < close, chunks))
            if len(chunks) != oldLen:
                alerts.append('Open contours cannot be imported')

            self.points += chunks # Add the now-closed contours to the poly list

            self.pointsChanged.emit()

            if len(alerts) > 0:
                QApplication.instance().outputMessage('\n'.join(alerts), "DXF import warnings")
