from PyQt5.QtWidgets import QMainWindow, QLabel, QSizePolicy, QApplication 
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np

import motorlib

class GrainImageWidget(QLabel):
    def __init__(self):
        super().__init__()

    def showImage(self, image):
        np.ma.set_fill_value(image, 0)
        image = np.logical_not(image.filled())
        image = image.astype(np.uint8) * 255
        height, width = image.shape
        bytesPerLine = width
        qImg = QImage(image.data, width, height, QImage.Format_Grayscale8)
        pixmap = QPixmap(qImg)
        self.setPixmap(pixmap)
