from PyQt5.QtWidgets import QWidget
from ..views.TabularEditor_ui import Ui_TabularEditor

class TabularEditor(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_TabularEditor()
        self.ui.setupUi(self)
        self.preferences = None

    def setPreferences(self, pref):
        self.preferences = pref

    def addTab(self, propDict):
        from .propellantEditor import PropellantEditor
        tab = PropellantEditor(self)
        tab.setPreferences(self.preferences)
        tab.loadProperties(propDict)
        self.ui.stackedWidget.insertWidget(0, tab)
        self.ui.stackedWidget.setCurrentIndex(0)

        tab2 = PropellantEditor(self)
        tab2.setPreferences(self.preferences)
        tab2.loadProperties(propDict)
        self.ui.stackedWidget.insertWidget(1, tab2)
        self.ui.stackedWidget.setCurrentIndex(1)
