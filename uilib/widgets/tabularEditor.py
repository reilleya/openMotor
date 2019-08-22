from PyQt5.QtWidgets import QWidget

from motorlib.propellant import PropellantTab

from ..views.TabularEditor_ui import Ui_TabularEditor

class TabularEditor(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_TabularEditor()
        self.ui.setupUi(self)
        self.preferences = None
        self.tabs = []

        self.ui.pushButtonAdd.pressed.connect(self.newTab)
        self.ui.pushButtonLeft.pressed.connect(lambda: self.changeIndex(-1))
        self.ui.pushButtonRight.pressed.connect(lambda: self.changeIndex(1))

    def setPreferences(self, pref):
        self.preferences = pref

    def addTab(self, propDict):
        from .propellantEditor import PropellantEditor
        self.tabs.append(PropellantEditor(self))
        self.tabs[-1].setPreferences(self.preferences)
        self.tabs[-1].loadProperties(propDict)
        self.ui.stackedWidget.insertWidget(len(self.tabs) - 1, self.tabs[-1])
        self.ui.stackedWidget.setCurrentIndex(len(self.tabs) - 1)
        self.updateButtons()

    def getTabs(self):
        return [tab.getProperties() for tab in self.tabs]

    def updateButtons(self):
        self.ui.pushButtonLeft.setEnabled(self.ui.stackedWidget.currentIndex() != 0)
        self.ui.pushButtonRight.setEnabled(self.ui.stackedWidget.currentIndex() != len(self.tabs) - 1)
        self.ui.pushButtonRemove.setEnabled(len(self.tabs) > 1)

    def changeIndex(self, rel):
        self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() + rel)
        self.updateButtons()

    def newTab(self):
        from .propellantEditor import PropellantEditor
        self.tabs.append(PropellantEditor(self))
        self.tabs[-1].setPreferences(self.preferences)
        self.tabs[-1].loadProperties(PropellantTab())
        self.ui.stackedWidget.insertWidget(len(self.tabs) - 1, self.tabs[-1])
        self.ui.stackedWidget.setCurrentIndex(len(self.tabs) - 1)
        self.updateButtons()
