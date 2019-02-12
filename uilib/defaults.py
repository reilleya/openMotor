import motorlib

def defaultMotor():
    dm = motorlib.motor()
    bg = motorlib.batesGrain()
    bg.setProperties({'diameter': 0.083058, 
              'length': 0.1397, 
              'coreDiameter': 0.03175, 
              'inhibitedEnds': 0
              })
    bg2 = motorlib.batesGrain()
    bg2.setProperties({'diameter': 0.083058, 
              'length': 0.1397, 
              'coreDiameter': 0.03175, 
              'inhibitedEnds': 0
              })
    dm.grains.append(bg)
    dm.grains.append(bg2)

    dm.nozzle.setProperties({'throat': 0.014, 'exit': 0.03, 'efficiency': 0.9})
    dm.propellant.setProperties({'name': 'Cherry Limeade', 'density': 1680, 'a': 3.517054143255937e-05, 'n': 0.3273, 't': 3500, 'm': 23.67, 'k': 1.21})

    return dm
