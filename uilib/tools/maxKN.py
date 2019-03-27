from .. import tool

import motorlib

class maxKNTool(tool):
    def __init__(self, manager):
        props = {'kn': motorlib.floatProperty('KN', '', 0, 1000)}
        super().__init__(manager,
                            'Max KN', 
                            'Use this tool to set the nozzle throat to keep the KN below a certain value during the burn.',
                            props,
                            True)

    def applyChanges(self, inp, motor, sim):
        surfArea = sim.getPeakKN() * motorlib.geometry.circleArea(motor.nozzle.props['throat'].getValue())
        throatArea = surfArea / inp['kn']
        motor.nozzle.props['throat'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea))
        self.manager.updateMotor(motor)
