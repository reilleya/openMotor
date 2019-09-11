"""Provides default properties for the UI."""

from motorlib.motor import Motor
from motorlib.grains import BatesGrain
from motorlib.propellant import Propellant

CLPROPS = {'name': 'Cherry Limeade',
           'density': 1680,
           'a': 3.517054143255937e-05,
           'n': 0.3273,
           't': 3500,
           'm': 23.67,
           'k': 1.21
           }


def defaultMotor():
    defMotor = Motor()
    grain = BatesGrain()
    grain.setProperties({'diameter': 3.27 / 39.37,
                         'length': 5.5 / 39.37,
                         'coreDiameter': 1.25 / 39.37,
                         'inhibitedEnds': 'Neither'
                         })
    defMotor.grains.append(grain)
    defMotor.grains.append(grain)

    defMotor.nozzle.setProperties({'throat': 0.55/39.37, 'exit': 1.5/39.37, 'efficiency': 0.85})
    defMotor.propellant.setProperties(CLPROPS)

    return defMotor


def defaultPreferencesDict():
    prefDict = {}
    prefDict['general'] = {
        'maxPressure': 1500 * 6895,
        'maxMassFlux': 2 / 0.001422,
        'minPortThroat': 2,
        'burnoutWebThres': 0.01 / 39.37,
        'burnoutThrustThres': 0.1,
        'timestep': 0.03,
        'ambPressure': 101325,
        'mapDim': 750
    }
    prefDict['units'] = {
        'm': 'in',
        'm/s': 'ft/s',
        'Pa': 'psi',
        'kg': 'lb',
        'kg/m^3': 'lb/in^3',
        'kg/s': 'lb/s',
        'kg/(m^2*s)': 'lb/(in^2*s)',
        'm/(s*Pa^n)': 'in/(s*psi^n)',
        'm^3':'in^3'
    }
    return prefDict


def defaultPropellants():
    clProp = Propellant()
    clProp.setProperties(CLPROPS)

    owProps = {'name': 'Ocean Water',
               'density': 1650,
               'a': 1.467e-05,
               'n': 0.382,
               't': 3500,
               'm': 23.67,
               'k': 1.25}

    owProp = Propellant()
    owProp.setProperties(owProps)

    return [clProp, owProp]
