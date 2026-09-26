import unittest
import motorlib.motor
import motorlib.grains
import motorlib.propellant

class TestMotorMethods(unittest.TestCase):

    def test_calcKN(self):
        tm = motorlib.motor.Motor()
        tc = motorlib.motor.MotorConfig()

        bg = motorlib.grains.BatesGrain()
        bg.setProperties({
            'diameter': 0.083058,
            'length': 0.1397,
            'coreDiameter': 0.05,
            'inhibitedEnds': 'Neither'
        })

        tm.grains.append(bg)
        bg.simulationSetup(tc)
        tm.nozzle.setProperties({'throat': 0.01428})

        self.assertAlmostEqual(tm.calcKN([0], 0), 180, 0)
        self.assertAlmostEqual(tm.calcKN([0.0025], 0), 183, 0)
        self.assertAlmostEqual(tm.calcKN([0.005], 0), 185, 0)

    def test_calcPressure(self):
        tm = motorlib.motor.Motor()
        tc = motorlib.motor.MotorConfig()

        bg = motorlib.grains.BatesGrain()
        bg.setProperties({
            'diameter': 0.083058,
            'length': 0.1397,
            'coreDiameter': 0.05,
            'inhibitedEnds': 'Neither'
        })

        tm.grains.append(bg)
        bg.simulationSetup(tc)

        tm.nozzle.setProperties({'throat': 0.01428})
        tm.propellant = motorlib.propellant.Propellant()
        tm.propellant.setProperties({
            'name': 'KNSU',
            'density': 1890,
            'tabs': [
                {
                    'a': 0.000101,
                    'n': 0.319,
                    't': 1720,
                    'm': 41.98,
                    'k': 1.133
                }
            ]
        })
        self.assertAlmostEqual(tm.calcIdealPressure([0], 0), 4050196, 0)

    def test_transient_pressure_moves_toward_equilibrium(self):
        tm = motorlib.motor.Motor()
        bg = motorlib.grains.BatesGrain()
        bg.setProperties({
            'diameter': 0.083058,
            'length': 0.1397,
            'coreDiameter': 0.05,
            'inhibitedEnds': 'Neither'
        })
        tm.grains.append(bg)
        bg.simulationSetup(tm.config)
        tm.nozzle.setProperties({'throat': 0.01428})
        tm.propellant = motorlib.propellant.Propellant({
            'name': 'KNSU',
            'density': 1890,
            'tabs': [{
                'minPressure': 0,
                'maxPressure': 7e7,
                'a': 0.000101,
                'n': 0.319,
                't': 1720,
                'm': 41.98,
                'k': 1.133
            }]
        })

        equilibrium = tm.calcIdealPressure([0], 0)
        lowPressure = equilibrium / 2
        highPressure = equilibrium * 2

        self.assertGreater(tm.calcPressureRate([0], 0, lowPressure), 0)
        self.assertLess(tm.calcPressureRate([0], 0, highPressure), 0)
        self.assertGreater(
            tm.integratePressure([0], 0, lowPressure, 0.001), lowPressure
        )
        self.assertLess(
            tm.integratePressure([0], 0, highPressure, 0.001), highPressure
        )

if __name__ == '__main__':
    unittest.main()
