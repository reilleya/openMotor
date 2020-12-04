import unittest

from openMotor.motorlib.motor import Motor, MotorConfig
from openMotor.motorlib.grains import BatesGrain
from openMotor.motorlib.propellant import Propellant

class TestMotorMethods(unittest.TestCase):

    def test_calcKN(self):
        tm = Motor()
        tc = MotorConfig()

        bg = BatesGrain()
        bg.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'inhibitedEnds':'Neither'
                  })

        tm.grains.append(bg)
        bg.simulationSetup(tc)
        tm.nozzle.setProperties({'throat': 0.01428})

        self.assertAlmostEqual(tm.calcKN([0], 0), 180, 0)
        self.assertAlmostEqual(tm.calcKN([0.0025], 0), 183, 0)
        self.assertAlmostEqual(tm.calcKN([0.005], 0), 185, 0)


    def test_calcPressure(self):
        tm = Motor()
        tc = MotorConfig()

        bg = BatesGrain()
        bg.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'inhibitedEnds':'Neither'
                  })

        tm.grains.append(bg)
        bg.simulationSetup(tc)

        tm.nozzle.setProperties({'throat': 0.01428})
        tm.propellant = Propellant()
        tm.propellant.setProperties({
                    'name': 'KNSU',
                    'density': 1890, 
                    'tabs':[
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

from openMotor.motorlib import geometry
class TestGeometryMethods(unittest.TestCase):
    def test_circleArea(self):
        self.assertAlmostEqual(geometry.circleArea(0.5), 0.19634954)

    def test_circlePerimeter(self):
        self.assertAlmostEqual(geometry.circlePerimeter(0.5), 1.57079633)

    def test_circleDiameterFromArea(self):
        self.assertAlmostEqual(geometry.circleDiameterFromArea(0.19634954), 0.5)

    def test_tubeArea(self):
        self.assertAlmostEqual(geometry.tubeArea(0.5, 2), 3.14159265)

    def test_cylinderArea(self):
        self.assertAlmostEqual(geometry.cylinderArea(0.5, 2), 3.53429174)

    def test_cylinderVolume(self):
        self.assertAlmostEqual(geometry.cylinderVolume(0.5, 2), 0.39269908)

    def test_dist(self):
        self.assertEqual(geometry.dist((5, 5), (5, 5)), 0)
        self.assertEqual(geometry.dist((5, 5), (6, 5)), 1)
        self.assertEqual(geometry.dist((5, 5), (5, 6)), 1)
        self.assertEqual(geometry.dist((0, 0), (-1, -1)), 2 ** 0.5)

from openMotor.motorlib.nozzle import Nozzle, eRatioFromPRatio
class TestNozzleMethods(unittest.TestCase):
    def test_expansionRatioFromPressureRatio(self):
        self.assertAlmostEqual(eRatioFromPRatio(1.15, 0.0156), 0.10650602)

    def test_expansionRatio(self):
        nozzle = Nozzle()
        nozzle.setProperties({
            'throat': 0.1,
            'exit': 0.2,
        })
        self.assertAlmostEqual(nozzle.calcExpansion(), 4.0)
        nozzle.setProperties({
            'throat': 0.1,
            'exit': 0.3,
        })
        self.assertAlmostEqual(nozzle.calcExpansion(), 9.0)

    def test_getExitPressure(self):
        nozzle = Nozzle()
        nozzle.setProperties({
            'throat': 0.1,
            'exit': 0.2,
        })
        self.assertAlmostEqual(nozzle.getExitPressure(1.25, 5e6), 197579.76030584713)
        nozzle.setProperties({
            'throat': 0.1,
            'exit': 0.3,
        })
        self.assertAlmostEqual(nozzle.getExitPressure(1.25, 5e6), 63174.14300487552)
        self.assertAlmostEqual(nozzle.getExitPressure(1.2, 5e6), 72087.22454540983)
        self.assertAlmostEqual(nozzle.getExitPressure(1.2, 6e6), 86504.66945449157)

from openMotor.motorlib.propellant import Propellant
class TestPropellantMethods(unittest.TestCase):
    def test_proper_propellant_ranges(self):
        props = {'name': 'TestProp',
                   'density': 1650,
                   'tabs': [
                       {
                           'minPressure': 0,
                           'maxPressure': 6.895e+06,
                           'a': 1.467e-05,
                           'n': 0.382,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       }
                   ]
                  }
        testProp = Propellant(props)
        self.assertEqual(len(testProp.getErrors()), 0)

    def test_backwards_pressure_ranges(self):
        props = {'name': 'TestProp',
                   'density': 1650,
                   'tabs': [
                       {
                           'minPressure': 6.895e+06,
                           'maxPressure': 0,
                           'a': 1.467e-05,
                           'n': 0.382,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       },
                       {
                           'minPressure': 6.895e+06,
                           'maxPressure': 1.379e+07,
                           'a': 1.467e-05,
                           'n': 0.382,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       }
                   ]
                  }
        testProp = Propellant(props)
        self.assertIn('Tab #1 has reversed pressure limits.', [err.description for err in testProp.getErrors()])

    def test_overlapping_pressure_ranges(self):
        props = {'name': 'TestProp',
                   'density': 1650,
                   'tabs': [
                       {
                           'minPressure': 0,
                           'maxPressure': 6.895e+06,
                           'a': 1.467e-05,
                           'n': 0.382,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       },
                       {
                           'minPressure': 6e+06,
                           'maxPressure': 1.379e+07,
                           'a': 1.467e-05,
                           'n': 0.382,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       }
                   ]
                  }
        testProp = Propellant(props)
        self.assertIn('Tabs #1 and #2 have overlapping ranges.', [err.description for err in testProp.getErrors()])

    def test_get_combustion_properties_in_range(self):
        props = {'name': 'TestProp',
                   'density': 1650,
                   'tabs': [
                       {
                           'minPressure': 0,
                           'maxPressure': 6.895e+06,
                           'a': 1.467e-05,
                           'n': 0.382,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       },
                       {
                           'minPressure': 6.895e+06,
                           'maxPressure': 1.379e+07,
                           'a': 1e-05,
                           'n': 0.3,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       }
                   ]
                  }
        testProp = Propellant(props)
        self.assertEqual(testProp.getCombustionProperties(8e5), (1.467e-05, 0.382, 1.25, 3500, 23.67))
        self.assertEqual(testProp.getCombustionProperties(8e6), (1e-05, 0.3, 1.25, 3500, 23.67))

    def test_get_combustion_properties_out_of_range(self):
        props = {'name': 'TestProp',
                   'density': 1650,
                   'tabs': [
                       {
                           'minPressure': 0,
                           'maxPressure': 6.895e+06,
                           'a': 1.467e-05,
                           'n': 0.382,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       },
                       {
                           'minPressure': 7e+06,
                           'maxPressure': 1.379e+07,
                           'a': 1e-05,
                           'n': 0.3,
                           't': 3500,
                           'm': 23.67,
                           'k': 1.25
                       }
                   ]
                  }
        testProp = Propellant(props)
        self.assertEqual(testProp.getCombustionProperties(6.9e5), (1.467e-05, 0.382, 1.25, 3500, 23.67))
        self.assertEqual(testProp.getCombustionProperties(8e10), (1e-05, 0.3, 1.25, 3500, 23.67))

unittest.main()
