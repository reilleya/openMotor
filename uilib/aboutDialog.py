from PyQt5.QtWidgets import QDialog


class aboutDialog(QDialog):
    def __init__(self, version):
        from .views.AboutDialog_ui import Ui_AboutDialog
        QDialog.__init__(self)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        self.ui.labelText.setText(self.ui.labelText.text().replace('###', version))
