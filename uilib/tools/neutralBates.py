import motorlib

from ..tool import Tool


class NeutralBatesTool(Tool):
    def __init__(self, manager):
        props = {'length': motorlib.properties.FloatProperty('Propellant length', 'm', 0, 10),
                 'diameter': motorlib.properties.FloatProperty('Propellant diameter', 'm', 0, 1),
                 'grainSpace': motorlib.properties.FloatProperty('Grain spacer length', 'm', 0, 1),
                 'Kn': motorlib.properties.FloatProperty('Initial Kn', '', 0, 1000)}

        super().__init__(manager,
                         'Neutral BATES Geometry',
                         'Use this tool to generate the geometry for a neutral BATES motor of a specified diameter and length. The length field should be the total length that the propellant fits into, including spacers.',
                         props,
                         False)

    def applyChanges(self, inp, motor, simulation):
        grainLength = (inp['diameter'] * 1.68) + inp['grainSpace']
        numGrains = inp['length'] // grainLength
        newMotor = motorlib.motor.Motor()
        for _ in range(0, int(numGrains)):
            newGrain = motorlib.grains.BatesGrain()
            newGrain.props['diameter'].setValue(inp['diameter'])
            newGrain.props['length'].setValue(grainLength - inp['grainSpace'])
            newGrain.props['coreDiameter'].setValue(inp['diameter'] * 0.35)
            newMotor.grains.append(newGrain)

        for grain in motor.grains:
            grain.simulationSetup(self.preferences) # Just in case this does something for BATES grains eventually

        surfArea = sum([g.getSurfaceAreaAtRegression(0) for g in newMotor.grains])
        throatArea = surfArea / inp['Kn']
        newMotor.nozzle.props['throat'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea))
        # Close enough to optimal for 14.7 PSI, should eventually optimize this
        newMotor.nozzle.props['exit'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea * 7))
        newMotor.nozzle.props['efficiency'].setValue(0.85)

        newMotor.config.setProperties(self.preferences.getDict()['general'])

        self.manager.updateMotor(newMotor)
