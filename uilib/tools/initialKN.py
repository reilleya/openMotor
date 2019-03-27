from .. import tool

import motorlib

class initialKNTool(tool):
    def __init__(self, manager):
        props = {'kn': motorlib.floatProperty('KN', '', 0, 1000)}
        super().__init__(manager,
                            'Initial KN', 
                            'Use this tool to set the nozzle throat to achieve a specific KN at startup.',
                            props,
                            False)

    def applyChanges(self, inp, motor, sim):
        for grain in motor.grains:
            grain.simulationSetup(self.preferences)
        surfArea = motor.calcKN([0 for grain in motor.grains]) * motorlib.geometry.circleArea(motor.nozzle.props['throat'].getValue())
        throatArea = surfArea / inp['kn']
        motor.nozzle.props['throat'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea))
        self.manager.updateMotor(motor)
