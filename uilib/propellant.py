import yaml

from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtCore import QObject, pyqtSignal

from motorlib import propertyCollection, floatProperty, enumProperty
from motorlib import unitLabels, getAllConversions, convert
from motorlib import propellant

from . import collectionEditor
from . import defaultPropellants
from . import loadFile, saveFile, fileTypes, getConfigPath


class propellantManager(QObject):

    updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.propellants = []
        self.loadPropellants()

        self.propMenu = propellantMenu(self)
        self.propMenu.closed.connect(self.updated.emit)

    def loadPropellants(self):
        try:
            propList = loadFile(getConfigPath() + 'propellants.yaml', fileTypes.PROPELLANTS)
            for propDict in propList:
                newProp = propellant()
                newProp.setProperties(propDict)
                self.propellants.append(newProp)
        except FileNotFoundError:
            self.propellants = defaultPropellants()
            self.savePropellants()

    def savePropellants(self):
        try:
            saveFile(getConfigPath() + 'propellants.yaml', [prop.getProperties() for prop in self.propellants], fileTypes.PROPELLANTS)
        except:
            print('Unable to save propellants!')

    def getNames(self):
        return [prop.getProperty('name') for prop in self.propellants]

    def getPropellantByName(self, name):
        return self.propellants[self.getNames().index(name)]

    def showMenu(self):
        self.propMenu.setupPropList()
        self.propMenu.show()

    def setPreferences(self, pref):
        self.propMenu.ui.propEditor.setPreferences(pref)

class propellantMenu(QDialog):

    propellantEdited = pyqtSignal(dict)
    closed = pyqtSignal()

    def __init__(self, manager):
        from .views.PropMenu_ui import Ui_PropellantDialog

        QDialog.__init__(self)
        self.ui = Ui_PropellantDialog()
        self.ui.setupUi(self)

        self.manager = manager

        self.setupPropList()
        self.ui.listWidgetPropellants.currentItemChanged.connect(self.propSelected)

        self.ui.propEditor.changeApplied.connect(self.propEdited)
        self.ui.propEditor.closed.connect(self.editorClosed)

        self.ui.pushButtonNewPropellant.pressed.connect(self.newPropellant)
        self.ui.pushButtonDelete.pressed.connect(self.deleteProp)
        self.ui.pushButtonEdit.pressed.connect(self.editProp)

        self.setupButtons()

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
        np = propellant()
        np.setProperties({'name': propName, 'density': 1680, 'a': 3.517054143255937e-05, 'n': 0.3273, 't': 2800, 'm': 23.67, 'k': 1.21})
        self.manager.propellants.append(np)
        self.setupPropList()
        self.setupButtons()
        self.manager.savePropellants()

    def deleteProp(self):
        del self.manager.propellants[self.ui.listWidgetPropellants.currentRow()]
        self.manager.savePropellants()
        self.setupPropList()
        self.setupButtons()

    def editProp(self):
        prop = self.manager.propellants[self.ui.listWidgetPropellants.currentRow()]
        self.ui.propEditor.loadProperties(prop)
        self.toggleButtons(True)

    def propEdited(self, propDict):
        propNames = self.manager.getNames()
        if propDict['name'] in propNames:
            if propNames.index(propDict['name']) != self.ui.listWidgetPropellants.currentRow():
                print("Can't duplicate a prop name!")
                return
        self.manager.propellants[self.ui.listWidgetPropellants.currentRow()].setProperties(propDict)
        self.setupPropList()
        self.manager.savePropellants()

    def propSelected(self):
        self.ui.pushButtonEdit.setEnabled(True)
        self.ui.pushButtonDelete.setEnabled(True)

    def editorClosed(self):
        self.toggleButtons(False)

    def toggleButtons(self, editing):
        self.ui.listWidgetPropellants.setEnabled(not editing)
        self.ui.pushButtonNewPropellant.setEnabled(not editing)
        self.ui.pushButtonEdit.setEnabled(not editing)
        self.ui.pushButtonDelete.setEnabled(not editing)
        self.ui.buttonBox.setEnabled(not editing)

    def close(self):
        super().close()
        self.toggleButtons(False)
        self.ui.propEditor.cleanup()
        self.closed.emit()

class propellantEditor(collectionEditor):
    def __init__(self, parent):
        super().__init__(parent, True)

        self.labelCStar = QLabel("Characteristic Velocity: -")
        self.labelCStar.hide()
        self.stats.addWidget(self.labelCStar)

    def propertyUpdate(self):
        k = self.propertyEditors['k'].getValue()
        t = self.propertyEditors['t'].getValue()
        m = self.propertyEditors['m'].getValue()
        r = 8314
        num = (k * r/m * t)**0.5
        denom = k * ((2/(k+1))**((k+1)/(k-1)))**0.5
        charVel = num / denom

        if self.preferences is not None:
            dispUnit = self.preferences.getUnit('m/s')
        else:
            dispUnit = 'm/s'

        self.labelCStar.setText('Characteristic Velocity: ' + str(int(convert(charVel, 'm/s', dispUnit))) + ' ' + dispUnit)

    def cleanup(self):
        self.labelCStar.hide()

        super().cleanup()

    def getProperties(self): # Override to change units on ballistic coefficient
        res = super().getProperties()
        coeffUnit = self.propertyEditors['a'].dispUnit
        if coeffUnit == 'in/(s*psi^n)':
            res['a'] *= 1/(6895**res['n'])
        return res

    def loadProperties(self, collection): # Override for ballisitc coefficient units
        props = collection.getProperties()
        # Convert the ballistic coefficient based on the exponent
        ballisticCoeffUnit = self.preferences.getUnit('m/(s*Pa^n)')
        if ballisticCoeffUnit == 'in/(s*psi^n)':
            props['a'] /= 1/(6895**props['n'])
        # Create a new propellant instance using the new A
        newProp = propellant()
        newProp.setProperties(props)
        super().loadProperties(newProp)
        self.labelCStar.show()
