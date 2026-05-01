import math
import itertools

from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFileDialog, QApplication
from PyQt6.QtCore import pyqtSignal

import ezdxf
import ezdxf.path
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

            close = 0.001 # Max distance between endpoints of adjacent segments

            alerts = []
            self.points = [] # Closed contours go here
            chunks = [] # Individual segments of lines or arcs go here

            for ent in msp:
                if ent.dxftype() == 'LINE':
                    point1 = (ent.dxf.end[0], ent.dxf.end[1])
                    point2 = (ent.dxf.start[0], ent.dxf.start[1])

                    chunks.append([point1, point2])

                elif ent.dxftype() == 'LWPOLYLINE':
                    with ent.points() as points:
                        self.points.append(points)

                elif ent.dxftype() in ('SPLINE', 'ELLIPSE', 'ARC', 'CIRCLE'):
                    p = ezdxf.path.make_path(ent)
                    pts = [(v.x, v.y) for v in p.flattening(0.01)]
                    if len(pts) < 2:
                        alerts.append('Skipped degenerate {} entity'.format(ent.dxftype()))
                    elif motorlib.geometry.dist(pts[0], pts[-1]) < close:
                        self.points.append(pts)
                    else:
                        chunks.append(pts)
                else:
                    alerts.append("Can't import entity of type: {}".format(ent.dxftype()))

            # Join together the segments in chunks to closed contours
            join = None
            while join != []:
                join = [] # Will be populated like [ida, idb, flipa, flipb] if there is work to do
                for (chunkId, chunk), (compChunkID, compChunk) in itertools.combinations(enumerate(chunks), 2):
                    if motorlib.geometry.dist(chunk[0], compChunk[-1]) < close:
                        join = [compChunkID, chunkId, False, False]
                        break
                    elif motorlib.geometry.dist(chunk[-1], compChunk[0]) < close:
                        join = [chunkId, compChunkID, False, False]
                        break
                    elif motorlib.geometry.dist(chunk[-1], compChunk[-1]) < close:
                        join = [chunkId, compChunkID, False, True]
                        break
                    elif motorlib.geometry.dist(chunk[0], compChunk[0]) < close:
                        join = [chunkId, compChunkID, True, False]
                        break
                if join != []: # Connect the chunks
                    firstChunk = chunks[join[0]]
                    secondChunk = chunks[join[1]]
                    if join[2]:
                        firstChunk.reverse()
                    if join[3]:
                        secondChunk.reverse()
                    chunks[join[0]] = firstChunk + secondChunk
                    del chunks[join[1]]

            oldLen = len(chunks)
            chunks = list(filter(lambda chunk: motorlib.geometry.dist(chunk[0], chunk[-1]) < close, chunks))
            if len(chunks) != oldLen:
                alerts.append('Open contours cannot be imported')

            self.points += chunks # Add the now-closed contours to the poly list

            self.pointsChanged.emit()

            if len(alerts) > 0:
                QApplication.instance().outputMessage('\n'.join(alerts), "DXF import warnings")
