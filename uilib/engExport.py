from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from motorlib.properties import PropertyCollection, FloatProperty, StringProperty

class ENGSettings(PropertyCollection):
    def __init__(self):
        super().__init__()
        self.props['diameter'] = FloatProperty('Motor Diameter', 'm', 0, 1)
        self.props['length'] = FloatProperty('Motor Length', 'm', 0, 2)
        self.props['hardwareMass'] = FloatProperty('Hardware Mass', 'kg', 0, 1000)
        self.props['designation'] = StringProperty('Motor Designation')
        self.props['manufacturer'] = StringProperty('Motor Manufacturer')

class ENGExportMenu(QDialog):
    def __init__(self):
        from .views.EngExporter_ui import Ui_EngExporterDialog

        QDialog.__init__(self)
        self.ui = Ui_EngExporterDialog()
        self.ui.setupUi(self)

        self.motorDesignation = ''
        self.times = None
        self.thrustCurve = None
        self.propMass = None
        self.ui.buttonBox.accepted.connect(self.exportEng)

    def exportEng(self):
        path = QFileDialog.getSaveFileName(None, 'Save motor', '', 'RASP Files (*.eng)')[0]
        if path is not None and path != '':
            if path[-4:] != '.eng':
                path += '.eng'

            with open(path, 'w') as outFile:
                stats = self.ui.motorStats.getProperties()
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
        self.ui.motorStats.setPreferences(pref)

    def open(self):
        newSettings = ENGSettings()
        newSettings.setProperties({'designation': self.motorDesignation})
        self.ui.motorStats.loadProperties(newSettings)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.times is not None)
        self.show()

    def acceptSimResult(self, simRes):
        self.motorDesignation = simRes.getDesignation()
        self.times = simRes.channels['time'].getData()
        self.thrustCurve = simRes.channels['force'].getData()
        self.thrustCurve[0] += 0.01
        self.propMass = simRes.getPropellantMass()
