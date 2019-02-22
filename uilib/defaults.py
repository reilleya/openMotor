import motorlib

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
    dm.propellant.setProperties({'name': 'Cherry Limeade', 'density': 1680, 'a': 3.517054143255937e-05, 'n': 0.3273, 't': 3500, 'm': 23.67, 'k': 1.21})

    return dm
