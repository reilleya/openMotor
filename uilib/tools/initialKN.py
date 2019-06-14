import motorlib

from ..tool import Tool


class InitialKNTool(Tool):
    def __init__(self, manager):
        props = {'Kn': motorlib.properties.floatProperty('Kn', '', 0, 1000)}
        super().__init__(manager,
                         'Initial Kn',
                         'Use this tool to set the nozzle throat to achieve a specific Kn at startup.',
                         props,
                         False)

    def applyChanges(self, inp, motor, simulation):
        for grain in motor.grains:
            grain.simulationSetup(self.preferences)
        surfArea = motor.calcKN([0 for grain in motor.grains]) * motorlib.geometry.circleArea(motor.nozzle.props['throat'].getValue())
        throatArea = surfArea / inp['Kn']
        motor.nozzle.props['throat'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea))
        self.manager.updateMotor(motor)
