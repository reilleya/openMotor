from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import xml.etree.ElementTree as ET

import motorlib

# BS type -> oM class for all grains we can import
supportedGrainTable = {
                '1': motorlib.grains.batesGrain,
                '2': motorlib.grains.dGrain,
                '3': motorlib.grains.moonBurner,
                '5': motorlib.grains.cGrain,
                '6': motorlib.grains.xCore,
                '7': motorlib.grains.finocyl 
             }

# BS type -> label for grains we know about but can't import
unsupportedGrainTable = {
                '4': 'Star',
                '8': 'Tablet',
                '9': 'Pie Segment'
            }

# oM class -> BS type for grains we can export
exportTypeTable = {
                motorlib.grains.batesGrain: '1',
                motorlib.grains.endBurner: '1',
                motorlib.grains.dGrain: '2',
                motorlib.grains.moonBurner: '3',
                motorlib.grains.cGrain: '5',
                motorlib.grains.xCore: '6',
                motorlib.grains.finocyl: '7' 
            }

# Attributes for the root element of the BSX file
bsxMotorAttrib = {
                'Name': '',
                'DiameterMM': '0',
                'Length': '0',
                'Delays': '0',
                'HardwareWeight': '0',
                'MFGCode': '',
                'ThrustMethod': '1',
                'ThrustCoefGiven': '1.2',
                'UnitsLinear': '1'
            }

# Converts a string containing a value in inches to a float of meters
def inToM(value):
    return motorlib.convert(float(value), 'in', 'm')

# Converts a float containing meters to a string of inches
def mToIn(value):
    return str(motorlib.convert(value, 'm', 'in'))

class burnsimManager(QObject):
    def __init__(self, fileManager):
        super().__init__()
        self.fileManager = fileManager

    # Open a dialog to pick the file to load and load it. Returns true if they load something, false otherwise
    def showImportMenu(self):
        if self.fileManager.unsavedCheck():
            path = QFileDialog.getOpenFileName(None, 'Import BurnSim motor', '', 'BurnSim Motor Files (*.bsx)')[0]
            if path != '' and path is not None:
                return self.importFile(path)
        return False

    # Open a dialog to pick the file to save to and dump the BSX version of the current motor to it
    def showExportMenu(self):
        path = QFileDialog.getSaveFileName(None, 'Export BurnSim motor', '', 'BurnSim Motor Files (*.bsx)')[0]
        if path == '' or path is None:
            return
        if path[-4:] != '.bsx':
            path += '.bsx'
        motor = self.fileManager.getCurrentMotor()
        self.exportFile(path, motor)

    # Show a dialog displaying some text
    def showWarning(self, text):
        msg = QMessageBox()
        msg.setText(text)
        msg.setWindowTitle("Warning")
        msg.exec_()

    # Opens the BSX file located at path, generates a motor from it, and starts motor history there
    def importFile(self, path):
        motor = motorlib.motor()
        tree = ET.parse(path)
        root = tree.getroot()
        errors = ''
        propSet = False
        for child in root:
            if child.tag == 'Nozzle':
                motor.nozzle.setProperty('throat', inToM(child.attrib['ThroatDia']))
                motor.nozzle.setProperty('exit', inToM(child.attrib['ExitDia']))
                motor.nozzle.setProperty('efficiency', float(child.attrib['NozzleEfficiency']) / 100)
            if child.tag == 'Grain':
                if child.attrib['Type'] in supportedGrainTable:
                    motor.grains.append(supportedGrainTable[child.attrib['Type']]())
                    motor.grains[-1].setProperty('diameter', inToM(child.attrib['Diameter']))
                    motor.grains[-1].setProperty('length', inToM(child.attrib['Length']))

                    grainType = child.attrib['Type']

                    if child.attrib['EndsInhibited'] == '1':
                        motor.grains[-1].setProperty('inhibitedEnds', 'Top')
                    elif child.attrib['EndsInhibited'] == '2':
                        motor.grains[-1].setProperty('inhibitedEnds', 'Both')

                    if grainType in ('1', '3', '7'): # Grains with core diameter
                        motor.grains[-1].setProperty('coreDiameter', inToM(child.attrib['CoreDiameter']))

                    if grainType == '2': # D grain specific properties
                        motor.grains[-1].setProperty('slotOffset', inToM(child.attrib['EdgeOffset']))

                    elif grainType == '3': # Moonburner specific properties
                        motor.grains[-1].setProperty('coreOffset', inToM(child.attrib['CoreOffset']))

                    elif grainType == '5': # C grain specific properties
                        motor.grains[-1].setProperty('slotWidth', inToM(child.attrib['SlotWidth']))
                        radius = motor.grains[-1].getProperty('diameter') / 2
                        motor.grains[-1].setProperty('slotOffset', radius - inToM(child.attrib['SlotDepth']))

                    elif grainType == '6': # X core specific properties
                        motor.grains[-1].setProperty('slotWidth', inToM(child.attrib['SlotWidth']))
                        motor.grains[-1].setProperty('slotLength', inToM(child.attrib['CoreDiameter']) / 2)

                    elif grainType == '7': # Finocyl specific properties
                        motor.grains[-1].setProperty('finWidth', inToM(child.attrib['FinWidth']))
                        motor.grains[-1].setProperty('finLength', inToM(child.attrib['FinLength']))
                        motor.grains[-1].setProperty('numFins', int(child.attrib['FinCount']))

                    if not propSet: # Use propellant numbers from the forward grain
                        impProp = child.find('Propellant')
                        propellant = motorlib.propellant()
                        propellant.setProperty('name', impProp.attrib['Name'])
                        n = float(impProp.attrib['BallisticN'])
                        a = float(impProp.attrib['BallisticA']) * 1/(6895**n)
                        propellant.setProperty('n', n)
                        propellant.setProperty('a', motorlib.convert(a, 'in/(s*psi^n)', 'm/(s*Pa^n)')) # Conversion only does in/s to m/s, the rest is handled above
                        propellant.setProperty('density', motorlib.convert(float(impProp.attrib['Density']), 'lb/in^3', 'kg/m^3'))
                        propellant.setProperty('k', float(impProp.attrib['SpecificHeatRatio']))
                        impMolarMass = impProp.attrib['MolarMass']
                        if impMolarMass == '0':
                            propellant.setProperty('m', 23.67) # If the user has entered 0, override it to match the default propellant.
                        else:
                            propellant.setProperty('m', float(impMolarMass))
                        propellant.setProperty('t', 3500) # Burnsim doesn't provide this property. Set it to match the default propellant.
                        motor.propellant = propellant
                        propSet = True

                else:
                    if child.attrib['Type'] in unsupportedGrainTable:
                        errors += "File contains a " + unsupportedGrainTable[child.attrib['Type']] + " grain, which can't be imported.\n"
                    else:
                        errors += "File contains an unknown grain of type " + child.attrib['Type'] + '.\n'
        
        if errors != '':
            self.showWarning(errors + '\nThe rest of the motor will be imported.')

        self.fileManager.startFromMotor(motor)
        return True

    # Takes a path to a bsx file and motor object and dumps the BSX version of the motor to the file
    def exportFile(self, path, motor):
        errors = ''

        outMotor = ET.Element('Motor')
        outMotor.attrib = bsxMotorAttrib

        outNozzle = ET.SubElement(outMotor, 'Nozzle')
        outNozzle.attrib['ThroatDia'] = mToIn(motor.nozzle.getProperty('throat'))
        outNozzle.attrib['ExitDia'] = mToIn(motor.nozzle.getProperty('exit'))
        outNozzle.attrib['NozzleEfficiency'] = str(int(motor.nozzle.getProperty('efficiency') * 100))
        outNozzle.attrib['AmbientPressure'] = '14.7'

        for gid, grain in enumerate(motor.grains):
            if type(grain) in exportTypeTable:
                outGrain = ET.SubElement(outMotor, 'Grain')
                outGrain.attrib['Type'] = exportTypeTable[type(grain)]
                outGrain.attrib['Propellant'] = motor.propellant.getProperty('name')
                outGrain.attrib['Diameter'] = mToIn(grain.getProperty('diameter'))
                outGrain.attrib['Length'] = mToIn(grain.getProperty('length'))

                if type(grain) is motorlib.grains.endBurner:
                    outGrain.attrib['CoreDiameter'] = '0'
                    outGrain.attrib['EndsInhibited'] = '1'
                else:
                    ends = grain.getProperty('inhibitedEnds')
                    if ends == 'Neither':
                        outGrain.attrib['EndsInhibited'] = '0'
                    elif ends in ('Top', 'Bottom'):
                        outGrain.attrib['EndsInhibited'] = '1'
                    else:
                        outGrain.attrib['EndsInhibited'] = '2'

                    if type(grain) in (motorlib.grains.batesGrain, motorlib.grains.finocyl, motorlib.grains.moonBurner): # Grains with core diameter
                        outGrain.attrib['CoreDiameter'] = mToIn(grain.getProperty('coreDiameter'))

                    if type(grain) is motorlib.grains.dGrain:
                        outGrain.attrib['EdgeOffset'] = mToIn(grain.getProperty('slotOffset'))

                    elif type(grain) is motorlib.grains.moonBurner:
                        outGrain.attrib['CoreOffset'] = mToIn(grain.getProperty('coreOffset'))

                    elif type(grain) is motorlib.grains.cGrain:
                        outGrain.attrib['SlotWidth'] = mToIn(grain.getProperty('slotWidth'))
                        radius = motor.grains[-1].getProperty('diameter') / 2
                        outGrain.attrib['SlotDepth'] = mToIn(grain.getProperty('slotOffset') - r)

                    elif type(grain) is motorlib.grains.xCore:
                        outGrain.attrib['SlotWidth'] = mToIn(grain.getProperty('slotWidth'))
                        outGrain.attrib['CoreDiameter'] = mToIn(2 * grain.getProperty('slotLength'))

                    elif type(grain) is motorlib.grains.finocyl:
                        outGrain.attrib['FinCount'] = str(grain.getProperty('numFins'))
                        outGrain.attrib['FinLength'] = mToIn(grain.getProperty('finLength'))
                        outGrain.attrib['FinWidth'] = mToIn(grain.getProperty('finWidth'))

                outProp = ET.SubElement(outGrain, 'Propellant')
                outProp.attrib['Name'] = motor.propellant.getProperty('name')
                a = motor.propellant.getProperty('a')
                n = motor.propellant.getProperty('n')
                a = motorlib.convert(a * (6895**n), 'm/(s*Pa^n)', 'in/(s*psi^n)')
                outProp.attrib['BallisticA'] = str(a)
                outProp.attrib['BallisticN'] = str(n)
                outProp.attrib['Density'] = str(motorlib.convert(motor.propellant.getProperty('density'), 'kg/m^3', 'lb/in^3'))
                outProp.attrib['SpecificHeatRatio'] = str(motor.propellant.getProperty('k'))
                outProp.attrib['MolarMass'] = str(motor.propellant.getProperty('m'))
                outProp.attrib['CombustionTemp'] = '0' # Unclear if this is used anyway
                ispStar = motor.propellant.getCStar() / 9.80665
                outProp.attrib['ISPStar'] = str(ispStar)

                outNotes = ET.SubElement(outProp, 'Notes')

            else:
                errors += "Can't export grain #" + str(gid + 1) + " because it has type " + grain.geomName + ".\n"

        outNotes = ET.SubElement(outMotor, 'MotorNotes')

        if errors != '':
            self.showWarning(errors + '\nThe rest of the motor will be exported.')

        with open(path, 'wb') as outFile:
            outFile.write(ET.tostring(outMotor))
