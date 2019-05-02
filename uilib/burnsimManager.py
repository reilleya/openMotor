from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import xml.etree.ElementTree as ET

import motorlib

supportedGrainTable = {
                '1': motorlib.grains.batesGrain,
                '2': motorlib.grains.dGrain,
                '3': motorlib.grains.moonBurner,
                '5': motorlib.grains.cGrain,
                '6': motorlib.grains.xCore,
                '7': motorlib.grains.finocyl 
             }

unsupportedGrainTable = {
                '4': 'Star',
                '8': 'Tablet',
                '9': 'Pie Segment'
            }

def inToM(value):
    return motorlib.convert(float(value), 'in', 'm')

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

    def showExportMenu(self):
        path = QFileDialog.getSaveFileName(None, 'Export BurnSim motor', '', 'BurnSim Motor Files (*.bsx)')[0]
        if path == '' or path is None:
            return
        if path[-4:] != '.bsx':
            path += '.bsx'

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
                        propellant.setProperty('m', 23.67) # BurnSim does't provide this value
                        propellant.setProperty('t', 3500) # Or this one. TODO: modulate this to make the ISP correct
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

    def exportFile(self):
        pass


