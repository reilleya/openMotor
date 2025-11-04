import unittest

import motorlib.motor
import motorlib.grains
import motorlib.propellant


class TestMotorMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.tm = motorlib.motor.Motor()
        self.tc = motorlib.motor.MotorConfig()

        self.bg = motorlib.grains.BatesGrain()
        self.bg.setProperties(
            {
                "diameter": 0.083058,
                "length": 0.1397,
                "coreDiameter": 0.05,
                "inhibitedEnds": "Neither",
            }
        )

        self.tm.grains.append(self.bg)
        self.bg.simulationSetup(self.tc)
        self.tm.nozzle.setProperties({"throat": 0.01428})

    def test_calcKN(self) -> None:
        self.assertAlmostEqual(self.tm.calcKN([0], 0), 180, 0)
        self.assertAlmostEqual(self.tm.calcKN([0.0025], 0), 183, 0)
        self.assertAlmostEqual(self.tm.calcKN([0.005], 0), 185, 0)

    def test_calcPressure(self) -> None:
        self.tm.propellant = motorlib.propellant.Propellant()
        self.tm.propellant.setProperties(
            {
                "name": "KNSU",
                "density": 1890,
                "tabs": [
                    {"a": 0.000101, "n": 0.319, "t": 1720, "m": 41.98, "k": 1.133}
                ],
            }
        )
        self.assertAlmostEqual(self.tm.calcIdealPressure([0], 0), 4050196, 0)


if __name__ == "__main__":
    unittest.main()
