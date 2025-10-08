"""Expansion"""

from motorlib.geometry import circleArea, circleDiameterFromArea


from ..tool import Tool


class ExpansionTool(Tool):
    def __init__(self, manager):
        props = {}
        super().__init__(
            manager,
            "Nozzle Expansion",
            "Use this tool to set the nozzle exit diameter to optimize expansion for your configured ambient pressure.",
            props,
            True,
        )

    def applyChanges(self, inp, motor, simulation):
        _, _, k, _, _ = motor.propellant.getCombustionProperties(
            simulation.getAveragePressure()
        )
        pRatio = (
            motor.config.props["ambPressure"].getValue()
            / simulation.getAveragePressure()
        )

        aRatio = (
            ((k + 1) / 2) ** (1 / (k - 1))
            * pRatio ** (1 / k)
            * (((k + 1) / (k - 1)) * (1 - (pRatio ** ((k - 1) / k)))) ** 0.5
        )

        exitArea = circleArea(motor.nozzle.props["throat"].getValue()) / aRatio

        motor.nozzle.props["exit"].setValue(circleDiameterFromArea(exitArea))
        self.manager.updateMotor(motor)
