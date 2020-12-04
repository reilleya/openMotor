from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QPixmap
from ..views.AboutDialog_ui import Ui_AboutDialog


class AboutDialog(QDialog):
    def __init__(self, version):
        QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        self.setWindowIcon(QApplication.instance().icon)
        self.ui.labelImage.setPixmap(QPixmap("resources/oMIconCyclesSmall.png"))

        self.ui.labelText.setText(self.ui.labelText.text().replace('###', version))
