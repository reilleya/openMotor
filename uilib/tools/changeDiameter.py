import motorlib

from ..tool import Tool


class ChangeDiameterTool(Tool):
    def __init__(self, manager):
        props = {'diameter': motorlib.properties.FloatProperty('Diameter', 'm', 0, 1)}
        super().__init__(manager,
                         'Motor diameter',
                         'Use this tool to set the diameter of all grains in the motor.',
                         props,
                         False)

    def applyChanges(self, inp, motor, simulation):
        for grain in motor.grains:
            grain.setProperties({'diameter': inp['diameter']})
        self.manager.updateMotor(motor)
