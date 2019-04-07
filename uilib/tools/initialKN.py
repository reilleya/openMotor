from .. import tool

import motorlib

class initialKNTool(tool):
    def __init__(self, manager):
        props = {'Kn': motorlib.floatProperty('Kn', '', 0, 1000)}
        super().__init__(manager,
                            'Initial Kn',
                            'Use this tool to set the nozzle throat to achieve a specific Kn at startup.',
                            props,
                            False)

    def applyChanges(self, inp, motor, sim):
        for grain in motor.grains:
            grain.simulationSetup(self.preferences)
        surfArea = motor.calcKN([0 for grain in motor.grains]) * motorlib.geometry.circleArea(motor.nozzle.props['throat'].getValue())
        throatArea = surfArea / inp['Kn']
        motor.nozzle.props['throat'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea))
        self.manager.updateMotor(motor)
