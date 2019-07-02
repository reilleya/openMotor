from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class GrainImageWidget(QLabel):
    def showImage(self, image):
        np.ma.set_fill_value(image, 0)
        image = np.logical_not(image.filled())
        image = image.astype(np.uint8) * 255
        height, width = image.shape
        qImg = QImage(image.data, width, height, QImage.Format_Grayscale8)
        pixmap = QPixmap(qImg)
        self.setPixmap(pixmap)
