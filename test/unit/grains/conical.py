import unittest
import motorlib.grains
from motorlib.enums.inhibitedEnds import InhibitedEnds


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
            'inhibitedEnds': InhibitedEnds.BOTH
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
            'inhibitedEnds': InhibitedEnds.BOTH
        }

        forwardFaceArea = 7.36310778e-05
        aftFaceArea = 7.53982236e-05
        lateralArea = 0.00070686055598659

        testGrain = motorlib.grains.ConicalGrain()
        testGrain.setProperties(properties)

        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea)
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0.001), 0.0013351790867045452)

        # For when uninibited conical grains work:
        """testGrain.setProperty('inhibitedEnds', InhibitedEnds.TOP)
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + aftFaceArea)

        testGrain.setProperty('inhibitedEnds', InhibitedEnds.BOTTOM)
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + forwardFaceArea)

        testGrain.setProperty('inhibitedEnds', InhibitedEnds.NEITHER)
        self.assertAlmostEqual(testGrain.getSurfaceAreaAtRegression(0), lateralArea + forwardFaceArea + aftFaceArea)"""

    def test_getVolumeAtRegression(self):
        properties = {
            'length': 0.1,
            'diameter': 0.01,
            'forwardCoreDiameter': 0.0025,
            'aftCoreDiameter': 0.002,
            'inhibitedEnds': InhibitedEnds.BOTH
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
            'inhibitedEnds': InhibitedEnds.BOTH
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

if __name__ == '__main__':
    unittest.main()
