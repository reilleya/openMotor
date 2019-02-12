import yaml

from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtCore import QObject, pyqtSignal

from motorlib import propertyCollection, floatProperty, enumProperty
from motorlib import unitLabels, getAllConversions, convert
from motorlib import propellant

from . import collectionEditor

class propellantManager(QObject):

    updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.propellants = []
        self.loadPropellants()

        self.propMenu = propellantMenu(self)
        self.propMenu.closed.connect(self.updated.emit)

    def loadDefaults(self):
        cl = propellant()
        cl.setProperties({'name': 'Cherry Limeade', 'density': 1680, 'a': 3.517054143255937e-05, 'n': 0.3273, 't': 3500, 'm': 23.67, 'k': 1.21})
        self.propellants.append(cl)
        ow = propellant()
        ow.setProperties({'name': 'Ocean Water', 'density': 1650, 'a': 1.467e-05, 'n': 0.382, 't': 3500, 'm': 23.67, 'k': 1.25})
        self.propellants.append(ow)

    def loadPropellants(self):
        try:
            with open('propellants.yaml', 'r') as propFile:
                for propDict in yaml.load(propFile):
                    newProp = propellant()
                    newProp.setProperties(propDict)
                    self.propellants.append(newProp)
        except FileNotFoundError:
            self.loadDefaults()
            self.savePropellants()

    def savePropellants(self):
        try:
            with open('propellants.yaml', 'w') as propFile:
                propDicts = [prop.getProperties() for prop in self.propellants]
                yaml.dump(propDicts, propFile)
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
        self.propMenu.propEditor.setPreferences(pref)

class propellantMenu(QDialog):

    propellantEdited = pyqtSignal(dict)
    closed = pyqtSignal()

    def __init__(self, manager):
        QDialog.__init__(self)
        loadUi("PropMenu.ui", self)

        self.manager = manager

        self.setupPropList()
        self.listWidgetPropellants.currentItemChanged.connect(self.propSelected)

        self.propEditor.changeApplied.connect(self.propEdited)
        self.propEditor.closed.connect(self.editorClosed)

        self.pushButtonNewPropellant.pressed.connect(self.newPropellant)
        self.pushButtonDelete.pressed.connect(self.deleteProp)
        self.pushButtonEdit.pressed.connect(self.editProp)

        self.setupButtons()

    def show(self):
        self.setupButtons()
        super().show()

    def setupButtons(self):
        self.pushButtonEdit.setEnabled(False)
        self.pushButtonDelete.setEnabled(False)

    def setupPropList(self):
        self.listWidgetPropellants.clear()
        self.listWidgetPropellants.addItems(self.manager.getNames())

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
        del self.manager.propellants[self.listWidgetPropellants.currentRow()]
        self.manager.savePropellants()
        self.setupPropList()
        self.setupButtons()

    def editProp(self):
        prop = self.manager.propellants[self.listWidgetPropellants.currentRow()]
        self.propEditor.loadProperties(prop)
        self.toggleButtons(True)

    def propEdited(self, propDict):
        propNames = self.manager.getNames()
        if propDict['name'] in propNames:
            if propNames.index(propDict['name']) != self.listWidgetPropellants.currentRow():
                print("Can't duplicate a prop name!")
                return
        self.manager.propellants[self.listWidgetPropellants.currentRow()].setProperties(propDict)
        self.setupPropList()
        self.manager.savePropellants()

    def propSelected(self):
        self.pushButtonEdit.setEnabled(True)
        self.pushButtonDelete.setEnabled(True)

    def editorClosed(self):
        self.toggleButtons(False)

    def toggleButtons(self, editing):
        self.listWidgetPropellants.setEnabled(not editing)
        self.pushButtonNewPropellant.setEnabled(not editing)
        self.pushButtonEdit.setEnabled(not editing)
        self.pushButtonDelete.setEnabled(not editing)
        self.buttonBox.setEnabled(not editing)

    def close(self):
        super().close()
        self.toggleButtons(False)
        self.propEditor.cleanup()
        self.closed.emit()

class propellantEditor(collectionEditor):
    def __init__(self, parent):
        super().__init__(parent, True)

        self.labelCStar = QLabel("Characteristic Velocity: -")
        self.labelCStar.hide()
        self.stats.addWidget(self.labelCStar)

    def update(self):
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

    def loadProperties(self, collection):
        super().loadProperties(collection)
        self.labelCStar.show()

    def cleanup(self):
        self.labelCStar.hide()

        super().cleanup()
