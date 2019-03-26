from .. import tool

import motorlib

class changeDiameterTool(tool):
    def __init__(self, manager):
        props = {'diameter': motorlib.floatProperty('Diameter', 'm', 0, 1)}
        super().__init__(manager,
                            'Change motor diameter', 
                            'Use this tool to set the diameter of all grains in the motor',
                            props)

    def applyChanges(self, inp):
        motor = self.manager.getMotor()
        for grain in motor.grains:
            grain.setProperties({'diameter': inp['diameter']})
        self.manager.updateMotor(motor)
