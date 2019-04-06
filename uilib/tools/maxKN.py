from .. import tool

import motorlib

class maxKNTool(tool):
    def __init__(self, manager):
        props = {'Kn': motorlib.floatProperty('Kn', '', 0, 1000)}
        super().__init__(manager,
                            'Max Kn',
                            'Use this tool to set the nozzle throat to keep the Kn below a certain value during the burn.',
                            props,
                            True)

    def applyChanges(self, inp, motor, sim):
        surfArea = sim.getPeakKN() * motorlib.geometry.circleArea(motor.nozzle.props['throat'].getValue())
        throatArea = surfArea / inp['Kn']
        motor.nozzle.props['throat'].setValue(motorlib.geometry.circleDiameterFromArea(throatArea))
        self.manager.updateMotor(motor)
