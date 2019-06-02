import motorlib

from .preferences import Preferences

CLPROPS = {'name': 'Cherry Limeade',
           'density': 1680,
           'a': 3.517054143255937e-05,
           'n': 0.3273,
           't': 3500,
           'm': 23.67,
           'k': 1.21
           }

def defaultMotor():
    defMotor = motorlib.motor()
    grain = motorlib.batesGrain()
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

def defaultPreferences():
    pref = Preferences()

    pref.general.props['burnoutWebThres'].setValue(0.01 / 39.37)
    pref.general.props['burnoutThrustThres'].setValue(0.1)
    pref.general.props['timestep'].setValue(0.03)
    pref.general.props['ambPressure'].setValue(101325)
    pref.general.props['mapDim'].setValue(750)

    pref.units.props['m'].setValue('in')
    pref.units.props['m/s'].setValue('ft/s')
    pref.units.props['Pa'].setValue('psi')
    pref.units.props['kg'].setValue('lb')
    pref.units.props['kg/m^3'].setValue('lb/in^3')
    pref.units.props['kg/s'].setValue('lb/s')
    pref.units.props['kg/(m^2*s)'].setValue('lb/(in^2*s)')
    pref.units.props['m/(s*Pa^n)'].setValue('in/(s*psi^n)')

    return pref

def defaultPropellants():

    clProp = motorlib.propellant()
    clProp.setProperties(CLPROPS)

    owProps = {'name': 'Ocean Water',
               'density': 1650,
               'a': 1.467e-05,
               'n': 0.382,
               't': 3500,
               'm': 23.67,
               'k': 1.25}

    owProp = motorlib.propellant()
    owProp.setProperties(owProps)

    return [clProp, owProp]
