from PyQt5.QtWidgets import QDialog
from .views.AboutDialog_ui import Ui_AboutDialog


class aboutDialog(QDialog):
    def __init__(self, version):
        QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        self.ui.labelText.setText(version)
