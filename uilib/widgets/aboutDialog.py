from PyQt6.QtWidgets import QDialog, QApplication
from ..views.AboutDialog_ui import Ui_AboutDialog


class AboutDialog(QDialog):
    def __init__(self, version):
        QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        self.setWindowIcon(QApplication.instance().icon)

        self.ui.labelText.setText(self.ui.labelText.text().replace('###', version))
