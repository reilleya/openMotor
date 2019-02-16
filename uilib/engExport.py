from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from PyQt5.uic import loadUi
from motorlib import propertyCollection, floatProperty, stringProperty
from . import collectionEditor

class engExportEditor(collectionEditor):
    def __init__(self, parent):
        super().__init__(parent, False)

class engSettings(propertyCollection):
    def __init__(self):
        super().__init__()
        self.props['diameter'] = floatProperty('Motor Diameter', 'm', 0, 1)
        self.props['length'] = floatProperty('Motor Length', 'm', 0, 2)
        self.props['hardwareMass'] = floatProperty('Hardware Mass', 'kg', 0, 1000)
        self.props['designation'] = stringProperty('Motor Designation')
        self.props['manufacturer'] = stringProperty('Motor Manufacturer')

class engExportMenu(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        loadUi('resources/EngExporter.ui', self)
        self.motorDesignation = ''
        self.times = None
        self.thrustCurve = None
        self.propMass = None
        self.buttonBox.accepted.connect(self.exportEng)

    def exportEng(self):
        path = QFileDialog.getSaveFileName(None, 'Save motor', '', 'RASP Files (*.eng)')[0]
        if path is not None and path != '':
            if path[-4:] != '.eng':
                path += '.eng'

            with open(path, 'w') as outFile:
                stats = self.motorStats.getProperties()
                contents = ' '.join([stats['designation'], 
                                   str(round(stats['diameter'] * 1000, 6)), 
                                   str(round(stats['length'] * 1000, 6)),
                                   'P',
                                   str(round(self.propMass, 6)),
                                   str(round(self.propMass + stats['hardwareMass'], 6)),
                                   stats['manufacturer']
                                   ]) + '\n'

                for time, force in zip(self.times, self.thrustCurve):
                    contents += str(round(time, 4)) + ' ' + str(round(force, 4)) + '\n'

                contents += ';'

                outFile.write(contents)

    def setPreferences(self, pref):
        self.motorStats.setPreferences(pref)

    def open(self):
        newSettings = engSettings()
        newSettings.setProperties({'designation': self.motorDesignation})
        self.motorStats.loadProperties(newSettings)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.times is not None)
        self.show()

    def acceptSimResult(self, simRes):
        self.motorDesignation = simRes.getDesignation()
        self.times = simRes.time
        self.thrustCurve = simRes.force
        self.thrustCurve[0] += 0.01
        self.propMass = sum([grain[0] for grain in simRes.mass])
