import unittest

import motorlib.motor
import motorlib.grains
import motorlib.propellant
class TestMotorMethods(unittest.TestCase):

    def test_calcKN(self):
        tm = motorlib.motor.Motor()
        tc = motorlib.motor.MotorConfig()

        bg = motorlib.grains.BatesGrain()
        bg.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'inhibitedEnds':'Neither'
                  })

        tm.grains.append(bg)
        bg.simulationSetup(tc)
        tm.nozzle.setProperties({'throat': 0.01428})

        self.assertAlmostEqual(tm.calcKN([0]), 180, 0)
        self.assertAlmostEqual(tm.calcKN([0.0025]), 183, 0)
        self.assertAlmostEqual(tm.calcKN([0.005]), 185, 0)


    def test_calcPressure(self):
        tm = motorlib.motor.Motor()
        tc = motorlib.motor.MotorConfig()

        bg = motorlib.grains.BatesGrain()
        bg.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'inhibitedEnds':'Neither'
                  })

        tm.grains.append(bg)
        bg.simulationSetup(tc)

        tm.nozzle.setProperties({'throat': 0.01428})
        tm.propellant = motorlib.propellant.Propellant()
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
        self.assertAlmostEqual(tm.calcIdealPressure([0], 0), 4050030, 0)

import motorlib.geometry
class TestGeometryMethods(unittest.TestCase):
    def test_circle(self):
        self.assertAlmostEqual(motorlib.geometry.circleArea(0.5), 0.19634954)

    def test_tubeArea(self):
        self.assertAlmostEqual(motorlib.geometry.tubeArea(0.5, 2), 3.14159265)

    def test_cylinderArea(self):
        self.assertAlmostEqual(motorlib.geometry.cylinderArea(0.5, 2), 3.53429174)

    def test_cylinderVolume(self):
        self.assertAlmostEqual(motorlib.geometry.cylinderVolume(0.5, 2), 0.39269908)

import motorlib.nozzle
class TestNozzleMethods(unittest.TestCase):
    def test_expansionRatio(self):
        self.assertAlmostEqual(motorlib.nozzle.eRatioFromPRatio(1.15, 0.0156), 0.10650602)

import motorlib.propellant
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
        testProp = motorlib.propellant.Propellant(props)
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
        testProp = motorlib.propellant.Propellant(props)
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
        testProp = motorlib.propellant.Propellant(props)
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
        testProp = motorlib.propellant.Propellant(props)
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
        testProp = motorlib.propellant.Propellant(props)
        self.assertEqual(testProp.getCombustionProperties(6.9e5), (1.467e-05, 0.382, 1.25, 3500, 23.67))
        self.assertEqual(testProp.getCombustionProperties(8e10), (1e-05, 0.3, 1.25, 3500, 23.67))

unittest.main()
