from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

class grainPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("resources/GrainPreview.ui", self)

    def loadGrain(self, grain):
        self.tab.showGrain(grain)
