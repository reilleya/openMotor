from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication
from PyQt5.QtCore import pyqtSignal
from ..helpers import FLAGS_NO_ICON
from PyQt5.QtCore import Qt

import motorlib.propellant

from ..views.PropMenu_ui import Ui_PropellantDialog
from ..logger import logger

class PropellantMenu(QDialog):

    propellantEdited = pyqtSignal(dict)
    closed = pyqtSignal()

    def __init__(self, manager):
        QDialog.__init__(self)
        self.ui = Ui_PropellantDialog()
        self.ui.setupUi(self)

        self.manager = manager

        self.setWindowIcon(QApplication.instance().icon)

        self.setupPropList()
        self.ui.listWidgetPropellants.currentItemChanged.connect(self.propSelected)

        self.ui.propEditor.changeApplied.connect(self.propEdited)
        self.ui.propEditor.closed.connect(self.editorClosed)

        self.ui.pushButtonNewPropellant.pressed.connect(self.newPropellant)
        self.ui.pushButtonDelete.pressed.connect(self.deleteProp)
        self.ui.pushButtonEdit.pressed.connect(self.editProp)

        self.ui.listWidgetPropellants.doubleClicked.connect(self.editProp)

        self.ui.propEditor.addButtons()

        self.setupButtons()

        self.editingPropellant = False

    def show(self):
        self.setupButtons()
        super().show()

    def setupButtons(self):
        self.ui.pushButtonEdit.setEnabled(False)
        self.ui.pushButtonDelete.setEnabled(False)

    def setupPropList(self):
        self.ui.listWidgetPropellants.clear()
        self.ui.listWidgetPropellants.addItems(self.manager.getNames())

    def newPropellant(self):
        propName = "New Propellant"
        if propName in self.manager.getNames():
            propNumber = 1
            while propName + " " + str(propNumber) in self.manager.getNames():
                propNumber += 1
            propName = propName + " " + str(propNumber)
        newProp = motorlib.propellant.Propellant()
        newProp.setProperty('name', propName)
        newPropTab = motorlib.propellant.PropellantTab()
        newProp.props['tabs'].addTab(newPropTab)
        self.manager.propellants.append(newProp)
        self.setupPropList()
        self.setupButtons()
        self.manager.savePropellants()
        self.ui.listWidgetPropellants.setCurrentRow(len(self.manager.propellants) - 1)
        self.editProp()

    def deleteProp(self):
        del self.manager.propellants[self.ui.listWidgetPropellants.currentRow()]
        self.manager.savePropellants()
        self.setupPropList()
        self.setupButtons()

    def editProp(self):
        prop = self.manager.propellants[self.ui.listWidgetPropellants.currentRow()]
        self.ui.propEditor.loadProperties(prop)
        self.toggleButtons(True)
        self.editingPropellant = True

    def propEdited(self, propDict):
        # If the name they choose matches an existing propellant, don't apply that change
        propNames = self.manager.getNames()
        if propDict['name'] in propNames:
            if propNames.index(propDict['name']) != self.ui.listWidgetPropellants.currentRow():
                logger.warn("Can't duplicate a propellant name!")
                del propDict['name']

        self.manager.propellants[self.ui.listWidgetPropellants.currentRow()].setProperties(propDict)
        self.setupPropList()
        self.manager.savePropellants()

    def propSelected(self):
        self.ui.pushButtonEdit.setEnabled(True)
        self.ui.pushButtonDelete.setEnabled(True)

    def editorClosed(self):
        self.editingPropellant = False
        self.toggleButtons(False)

    def toggleButtons(self, editing):
        self.ui.listWidgetPropellants.setEnabled(not editing)
        self.ui.pushButtonNewPropellant.setEnabled(not editing)
        self.ui.pushButtonEdit.setEnabled(not editing)
        self.ui.pushButtonDelete.setEnabled(not editing)

    def closeEvent(self, event=None):
        if not self.unsavedCheck():
            if event is not None:
                if not isinstance(event, bool):
                    event.ignore()
            return
        self.toggleButtons(False)
        self.ui.propEditor.cleanup()
        self.closed.emit()

    def unsavedCheck(self):
        if not self.editingPropellant:
            return True

        msg = QMessageBox()
        msg.setWindowFlags(FLAGS_NO_ICON);
        msg.setText("Close without saving current propellant?")
        msg.setWindowTitle("Close without saving?")
        msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        res = msg.exec_()
        if res == QMessageBox.Save:
            self.propEdited(self.ui.propEditor.getProperties())
            return True
        return res == QMessageBox.Discard

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            if len(self.ui.listWidgetPropellants.selectedItems()) != 0:
                self.deleteProp()
