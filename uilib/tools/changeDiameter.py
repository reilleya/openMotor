from motorlib.properties import FloatProperty

from ..tool import Tool
from motorlib.constants import maximumRefDiameter


class ChangeDiameterTool(Tool):
    def __init__(self, manager):
        props = {
            "diameter": motorlib.properties.FloatProperty(
                "Diameter", "m", 0, maximumRefDiameter
            )
        }
        super().__init__(
            manager,
            "Motor Diameter",
            "Use this tool to set the diameter of all grains in the motor.",
            props,
            False,
        )

    def applyChanges(self, inp, motor, simulation):
        for grain in motor.grains:
            grain.setProperties({"diameter": inp["diameter"]})
        self.manager.updateMotor(motor)
