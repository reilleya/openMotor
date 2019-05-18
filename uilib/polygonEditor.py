from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFileDialog
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

            self.pointsChanged.emit()
