from ..tool import Tool

import motorlib

class ExpansionTool(Tool):
    def __init__(self, manager):
        props = {}
        super().__init__(manager,
                            'Nozzle expansion', 
                            'Use this tool to set the nozzle exit diameter to optimize expansion for your configured ambient pressure.',
                            props,
                            True)

    def applyChanges(self, inp, motor, sim):
        k = motor.propellant.props['k'].getValue()
        pRatio = self.preferences.general.props['ambPressure'].getValue() / sim.getAveragePressure()

        aRatio = ((k + 1) / 2) ** (1 / (k - 1)) * pRatio ** (1 / k) * (((k + 1) / (k - 1)) * (1 - (pRatio ** ((k - 1) / k)))) ** 0.5 

        exitArea = motorlib.geometry.circleArea(motor.nozzle.props['throat'].getValue()) / aRatio

        motor.nozzle.props['exit'].setValue(motorlib.geometry.circleDiameterFromArea(exitArea))
        self.manager.updateMotor(motor)
