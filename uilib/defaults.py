import motorlib

from . import preferences

clProps = {'name': 'Cherry Limeade', 'density': 1680, 'a': 3.517054143255937e-05, 'n': 0.3273, 't': 3500, 'm': 23.67, 'k': 1.21}

def defaultMotor():
    dm = motorlib.motor()
    bg = motorlib.batesGrain()
    bg.setProperties({'diameter': 3.27/39.37, 
              'length': 5.5/39.37, 
              'coreDiameter': 1.25/39.37, 
              'inhibitedEnds': 'Neither'
              })
    dm.grains.append(bg)
    dm.grains.append(bg)

    dm.nozzle.setProperties({'throat': 0.55/39.37, 'exit': 1.5/39.37, 'efficiency': 0.85})
    dm.propellant.setProperties(clProps)

    return dm

def defaultPreferences():
    pref = preferences()

    pref.general.props['burnoutWebThres'].setValue(0.03 / 39.37)
    pref.general.props['burnoutThrustThres'].setValue(0.1)
    pref.general.props['timestep'].setValue(0.03)
    pref.general.props['ambPressure'].setValue(101325)

    pref.units.props['m'].setValue('in')
    pref.units.props['pa'].setValue('psi')

    return pref

def defaultPropellants():

    cl = motorlib.propellant()
    cl.setProperties(clProps)

    ow = motorlib.propellant()
    ow.setProperties({'name': 'Ocean Water', 'density': 1650, 'a': 1.467e-05, 'n': 0.382, 't': 3500, 'm': 23.67, 'k': 1.25})

    return [cl, ow]
