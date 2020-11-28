from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import pyqtSignal

from ..views.SimulatingDialog_ui import Ui_SimProgressDialog


class SimulationProgressDialog(QDialog):

    simulationCanceled = pyqtSignal()

    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_SimProgressDialog()
        self.ui.setupUi(self)

        self.setWindowIcon(QApplication.instance().icon)

        self.ui.buttonBox.rejected.connect(self.closeEvent)

    def show(self):
        self.ui.progressBar.setValue(0)
        super().show()

    def closeEvent(self, event=None):
        self.simulationCanceled.emit()
        self.close()

    def progressUpdate(self, progress):
        self.ui.progressBar.setValue(int(progress * 100))
