from .. import tool

import motorlib

class neutralBatesTool(tool):
    def __init__(self, manager):
        props = {'length': motorlib.floatProperty('Propellant length', 'm', 0, 10),
                 'diameter': motorlib.floatProperty('Propellant diameter', 'm', 0, 1),
                 'grainSpace': motorlib.floatProperty('Grain spacer length', 'm', 0, 1),
                 'kn': motorlib.floatProperty('Initial KN', '', 0, 1000)
        }
        super().__init__(manager,
                            'Neutral BATES Geometry', 
                            'Use this tool to generate the geometry for a neutral BATES motor of a specified diameter and length. The length field should be the total length that the propellant fits into, including spacers.',
                            props,
                            False)

    def applyChanges(self, inp, motor, sim):
        grainLength = (inp['diameter'] * 1.68) + inp['grainSpace']
        numGrains = inp['length'] // grainLength
        newMotor = motorlib.motor()
        for i in range(0, int(numGrains)):
            newGrain = motorlib.batesGrain()
            newGrain.props['diameter'].setValue(inp['diameter'])
            newGrain.props['length'].setValue(grainLength - inp['grainSpace'])
            newGrain.props['coreDiameter'].setValue(inp['diameter'] * 0.35)
            newMotor.grains.append(newGrain)

        for grain in motor.grains:
            grain.simulationSetup(self.preferences) # Just in case this does something for BATES grains eventually

        surfArea = sum([g.getSurfaceAreaAtRegression(0) for g in newMotor.grains])
        throatArea = surfArea / inp['kn']
        newMotor.nozzle.props['throat'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea))
        newMotor.nozzle.props['exit'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea * 7)) # Usually pretty close to optimal expansion. Should probably actually optimize it.
        newMotor.nozzle.props['efficiency'].setValue(0.85)

        newMotor.propellant = self.manager.getPropellantByName(self.manager.getPropellantNames()[0])

        self.manager.updateMotor(newMotor)
