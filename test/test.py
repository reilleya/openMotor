import unittest


#######################################################################################################################
###                                                   Motor Tests                                                   ###
#######################################################################################################################

import motorlib.motor
import motorlib.grains
import motorlib.propellant
class TestMotorMethods(unittest.TestCase):

    def test_calcKN(self):
        tm = motorlib.motor.Motor()
        tc = motorlib.motor.MotorConfig()

        bg = motorlib.grains.BatesGrain()
        bg.setProperties({'diameter': 0.083058,
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


#######################################################################################################################
###                                                 Geometry Tests                                                  ###
#######################################################################################################################

import motorlib.geometry
class TestGeometryMethods(unittest.TestCase):
    def test_circleArea(self):
        self.assertAlmostEqual(motorlib.geometry.circleArea(0.5), 0.19634954)

    def test_circlePerimeter(self):
        self.assertAlmostEqual(motorlib.geometry.circlePerimeter(0.5), 1.57079633)

    def test_circleDiameterFromArea(self):
        self.assertAlmostEqual(motorlib.geometry.circleDiameterFromArea(0.19634954), 0.5)

    def test_tubeArea(self):
        self.assertAlmostEqual(motorlib.geometry.tubeArea(0.5, 2), 3.14159265)

    def test_cylinderArea(self):
        self.assertAlmostEqual(motorlib.geometry.cylinderArea(0.5, 2), 3.53429174)

    def test_cylinderVolume(self):
        self.assertAlmostEqual(motorlib.geometry.cylinderVolume(0.5, 2), 0.39269908)

    def test_frustumLateralSurfaceArea(self):
        self.assertAlmostEqual(motorlib.geometry.frustumLateralSurfaceArea(2, 3, 5), 39.46576927)

    def test_frustumVolume(self):
        # Cone case
        self.assertAlmostEqual(motorlib.geometry.frustumVolume(0, 10, 10), 261.79938779)
        # Frustum case
        self.assertAlmostEqual(motorlib.geometry.frustumVolume(10, 30, 50), 17016.96020694)

    def test_splitFrustum(self):
        # Simple case
        self.assertAlmostEqual(motorlib.geometry.splitFrustum(1, 2, 4, 2), ((1, 1.5, 2), (1.5, 2, 2)))
        # Inverted case
        self.assertAlmostEqual(motorlib.geometry.splitFrustum(2, 1, 4, 2), ((2, 1.5, 2), (1.5, 1, 2)))
        # Make sure that the connected ends of the frustums line up
        upper, lower = motorlib.geometry.splitFrustum(1, 3, 3, 1)
        self.assertEqual(upper[1], lower[0])

    def test_dist(self):
        self.assertEqual(motorlib.geometry.dist((5, 5), (5, 5)), 0)
        self.assertEqual(motorlib.geometry.dist((5, 5), (6, 5)), 1)
        self.assertEqual(motorlib.geometry.dist((5, 5), (5, 6)), 1)
        self.assertEqual(motorlib.geometry.dist((0, 0), (-1, -1)), 2 ** 0.5)

import motorlib.nozzle
class TestNozzleMethods(unittest.TestCase):
    def test_expansionRatioFromPressureRatio(self):
        self.assertAlmostEqual(motorlib.nozzle.eRatioFromPRatio(1.15, 0.0156), 0.10650602)

    def test_expansionRatio(self):
        nozzle = motorlib.nozzle.Nozzle()
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
        nozzle = motorlib.nozzle.Nozzle()
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


#######################################################################################################################
###                                                Propellant Tests                                                 ###
#######################################################################################################################

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


#######################################################################################################################
###                                               Conical Grain Tests                                               ###
#######################################################################################################################

import motorlib.grains
class ConicalGrainMethods(unittest.TestCase):

    def test_isCoreInverted(self):
        inverted = motorlib.grains.ConicalGrain()
        inverted.setProperties({
          'length': 0.1,
          'diameter': 0.01,
          'forwardCoreDiameter': 0.0025,
          'aftCoreDiameter': 0.002,
        })
        regular = motorlib.grains.ConicalGrain()
        regular.setProperties({
          'length': 0.1,
          'diameter': 0.01,
          'forwardCoreDiameter': 0.003,
          'aftCoreDiameter': 0.004,
        })

        self.assertEqual(inverted.isCoreInverted(), True)
        self.assertEqual(regular.isCoreInverted(), False)

    def test_getFrustumInfo(self):
        properties = {
          'length': 0.1,
          'diameter': 0.01,
          'forwardCoreDiameter': 0.0025,
          'aftCoreDiameter': 0.002,
          'inhibitedEnds': 'Both'
        }

        testGrain = motorlib.grains.ConicalGrain()
        testGrain.setProperties(properties)

        unregressed = testGrain.getFrustumInfo(0)
        self.assertAlmostEqual(unregressed[0], properties['aftCoreDiameter'])
        self.assertAlmostEqual(unregressed[1], properties['forwardCoreDiameter'])
        self.assertAlmostEqual(unregressed[2], properties['length'])

        beforeHittingWall = testGrain.getFrustumInfo(0.001)
        self.assertAlmostEqual(beforeHittingWall[0], 0.003999993750029297)
        self.assertAlmostEqual(beforeHittingWall[1], 0.004499993750029296)
        self.assertAlmostEqual(beforeHittingWall[2], properties['length']) # Length hasn't changed yet

        hitWall = testGrain.getFrustumInfo(0.0038)
        self.assertAlmostEqual(hitWall[0], 0.009599976250111327)
        self.assertAlmostEqual(hitWall[1], properties['diameter']) # This end has burned all the way to the wall
        self.assertAlmostEqual(hitWall[2], 0.08000468749267584)

    def test_getSurfaceAreaAtRegression(self):
        properties = {
          'length': 0.1,
          'diameter': 0.01,
          'forwardCoreDiameter': 0.0025,
          'aftCoreDiameter': 0.002,
          'inhibitedEnds': 'Both'
        }

        forwardFaceArea = 7.36310778e-05
        aftFaceArea = 7.53982236e-05
        lateralArea = 0.00070686055598659

        testGrain = motorlib.grains.ConicalGrain()
        testGrain.setProperties(properties)

        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea)
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0.001), 0.0013351790867045452)

        # For when uninibited conical grains work:
        """testGrain.setProperty('inhibitedEnds', 'Top')
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + aftFaceArea)

        testGrain.setProperty('inhibitedEnds', 'Bottom')
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + forwardFaceArea)

        testGrain.setProperty('inhibitedEnds', 'Neither')
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + forwardFaceArea + aftFaceArea)"""

    def test_getVolumeAtRegression(self):
        properties = {
          'length': 0.1,
          'diameter': 0.01,
          'forwardCoreDiameter': 0.0025,
          'aftCoreDiameter': 0.002,
          'inhibitedEnds': 'Both'
        }

        testGrain = motorlib.grains.ConicalGrain()
        testGrain.setProperties(properties)

        self.assertAlmostEqual(testGrain.getVolumeAtRegression(0), 7.454737567580781e-06)
        self.assertAlmostEqual(testGrain.getVolumeAtRegression(0.001), 6.433724127569215e-06)
        self.assertAlmostEqual(testGrain.getVolumeAtRegression(0.0038), 2.480054353678591e-07)

    def test_getWebLeft(self):
        properties = {
          'length': 0.1,
          'diameter': 0.01,
          'forwardCoreDiameter': 0.0025,
          'aftCoreDiameter': 0.002,
          'inhibitedEnds': 'Both'
        }

        testGrain = motorlib.grains.ConicalGrain()
        testGrain.setProperties(properties)

        self.assertAlmostEqual(testGrain.getWebLeft(0), 0.004)
        self.assertAlmostEqual(testGrain.getWebLeft(0.001), 0.003)
        self.assertAlmostEqual(testGrain.getWebLeft(0.0038), 0.0002)

        testGrain.setProperty('forwardCoreDiameter', 0.002)
        testGrain.setProperty('aftCoreDiameter', 0.0025)
        self.assertAlmostEqual(testGrain.getWebLeft(0), 0.004)
        self.assertAlmostEqual(testGrain.getWebLeft(0.001), 0.003)
        self.assertAlmostEqual(testGrain.getWebLeft(0.0038), 0.0002)


unittest.main()
