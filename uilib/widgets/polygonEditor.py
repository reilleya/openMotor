from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
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

            alerts = []
            self.points = [] # Closed contours go here
            chunks = [] # Individual segments of lines or arcs go here

            for ent in msp:
                if ent.dxftype() == 'ARC':
                    arcPoints = 20 # Number of segments in the arc
                    part = []
                    sa = ent.dxf.start_angle
                    ea = ent.dxf.end_angle
                    if sa > ea: # This ensures that the angle step (ea - sa) is not negative
                        ea += 360
                    for i in range(0, arcPoints):
                        a = sa + ((ea - sa) * (i / (arcPoints - 1)))
                        px = ent.dxf.center[0] + (math.cos(a * math.pi / 180) * ent.dxf.radius)
                        py = ent.dxf.center[1] + (math.sin(a * math.pi / 180) * ent.dxf.radius)
                        part.append((px, py))

                    chunks.append(part)

                elif ent.dxftype() == 'CIRCLE':
                    part = []
                    circlePoints = 36 # Number of segments in the arc
                    for i in range(0, circlePoints):
                        a = 2 * math.pi * (i / circlePoints)
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
                self.showAlert(alerts)

    # Show a dialog displaying some text
    def showAlert(self, messages):
        msg = QMessageBox()
        msg.setText('\n'.join(messages))
        msg.setWindowTitle("DXF import warnings")
        msg.exec_()
