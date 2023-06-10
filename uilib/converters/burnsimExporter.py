import xml.etree.ElementTree as ET

from motorlib.enums.units.BurnRateCoefficientUnit import BurnRateCoefficientUnit
from motorlib.enums.units.DensityUnit import DensityUnit
from motorlib.enums.units.LengthUnit import LengthUnit
from motorlib.properties import PropertyCollection, FloatProperty, StringProperty
import motorlib
from ..converter import Exporter

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

# oM class -> BS type for grains we can export
EXPORT_TYPES = {
    motorlib.grains.BatesGrain: '1',
    motorlib.grains.EndBurningGrain: '1',
    motorlib.grains.DGrain: '2',
    motorlib.grains.MoonBurner: '3',
    motorlib.grains.CGrain: '5',
    motorlib.grains.XCore: '6',
    motorlib.grains.Finocyl: '7'
}


def mToIn(value):
    """Converts a float containing meters to a string of inches"""
    return str(motorlib.units.convert(value, LengthUnit.METER, LengthUnit.INCH))


class BurnSimExporter(Exporter):
    def __init__(self, manager):
        super().__init__(manager, 'BurnSim File',
                         'Exports the current motor for use in BurnSim 3.0', {'.bsx': 'BurnSim Files'})
        self.reqNotMet = "Current motor must have a propellant set to export as a BurnSim file."

    def doConversion(self, path, config):
        """Takes a path to a bsx file and motor object and dumps the BSX version of the motor to the file"""
        errors = ''
        motor = self.manager.motor

        outMotor = ET.Element('Motor')
        outMotor.attrib = bsxMotorAttrib

        outNozzle = ET.SubElement(outMotor, 'Nozzle')
        outNozzle.attrib['ThroatDia'] = mToIn(motor.nozzle.getProperty('throat'))
        outNozzle.attrib['ExitDia'] = mToIn(motor.nozzle.getProperty('exit'))
        outNozzle.attrib['NozzleEfficiency'] = str(int(motor.nozzle.getProperty('efficiency') * 100))
        outNozzle.attrib['AmbientPressure'] = '14.7'

        for gid, grain in enumerate(motor.grains):
            if type(grain) in EXPORT_TYPES:
                outGrain = ET.SubElement(outMotor, 'Grain')
                outGrain.attrib['Type'] = EXPORT_TYPES[type(grain)]
                outGrain.attrib['Propellant'] = motor.propellant.getProperty('name')
                outGrain.attrib['Diameter'] = mToIn(grain.getProperty('diameter'))
                outGrain.attrib['Length'] = mToIn(grain.getProperty('length'))

                if isinstance(grain, motorlib.grains.EndBurningGrain):
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
                    # Grains with core diameter
                    if type(grain) in (motorlib.grains.BatesGrain, motorlib.grains.Finocyl, motorlib.grains.MoonBurner):
                        outGrain.attrib['CoreDiameter'] = mToIn(grain.getProperty('coreDiameter'))

                    if isinstance(grain, motorlib.grains.DGrain):
                        outGrain.attrib['EdgeOffset'] = mToIn(grain.getProperty('slotOffset'))

                    elif isinstance(grain, motorlib.grains.MoonBurner):
                        outGrain.attrib['CoreOffset'] = mToIn(grain.getProperty('coreOffset'))

                    elif isinstance(grain, motorlib.grains.CGrain):
                        outGrain.attrib['SlotWidth'] = mToIn(grain.getProperty('slotWidth'))
                        radius = motor.grains[-1].getProperty('diameter') / 2
                        outGrain.attrib['SlotDepth'] = mToIn(grain.getProperty('slotOffset') - radius)

                    elif isinstance(grain, motorlib.grains.XCore):
                        outGrain.attrib['SlotWidth'] = mToIn(grain.getProperty('slotWidth'))
                        outGrain.attrib['CoreDiameter'] = mToIn(2 * grain.getProperty('slotLength'))

                    elif isinstance(grain, motorlib.grains.Finocyl):
                        outGrain.attrib['FinCount'] = str(grain.getProperty('numFins'))
                        outGrain.attrib['FinLength'] = mToIn(grain.getProperty('finLength'))
                        outGrain.attrib['FinWidth'] = mToIn(grain.getProperty('finWidth'))

                outProp = ET.SubElement(outGrain, 'Propellant')
                outProp.attrib['Name'] = motor.propellant.getProperty('name')
                # Have to pick a single pressure for output
                exportPressure = 5.17e6
                ballA, ballN, gamma, _, m = motor.propellant.getCombustionProperties(exportPressure)
                ballA = motorlib.units.convert(ballA * (6895 ** ballN),

                                               BurnRateCoefficientUnit.INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N)
                outProp.attrib['BallisticA'] = str(ballA)
                outProp.attrib['BallisticN'] = str(ballN)
                density = str(motorlib.units.convert(motor.propellant.getProperty('density'),
                                                     DensityUnit.KILOGRAM_PER_CUBIC_METER,
                                                     DensityUnit.POUND_PER_CUBIC_INCH))
                outProp.attrib['Density'] = density
                outProp.attrib['SpecificHeatRatio'] = str(gamma)
                outProp.attrib['MolarMass'] = str(m)
                outProp.attrib['CombustionTemp'] = '0'  # Unclear if this is used anyway
                ispStar = motor.propellant.getCStar(exportPressure) / 9.80665
                outProp.attrib['ISPStar'] = str(ispStar)
                # Add empty notes section
                ET.SubElement(outProp, 'Notes')

            else:
                errors += "Can't export grain #" + str(gid + 1) + " because it has type " + grain.geomName + ".\n"
        # Add empty notes section
        ET.SubElement(outMotor, 'MotorNotes')

        if errors != '':
            self.manager.app.outputMessage(errors + '\nThe rest of the motor will be exported.')

        with open(path, 'wb') as outFile:
            outFile.write(ET.tostring(outMotor))

    def checkRequirements(self):
        return self.manager.motor is not None and self.manager.motor.propellant is not None
