import unittest
import motorlib.grains


class ConicalGrainMethods(unittest.TestCase):

    def setUp(self) -> None:
        properties = {
            "length": 0.1,
            "diameter": 0.01,
            "forwardCoreDiameter": 0.0025,
            "aftCoreDiameter": 0.002,
            "inhibitedEnds": "Both",
        }
        self.testGrain = motorlib.grains.ConicalGrain()
        self.testGrain.setProperties(properties)

    def tearDown(self) -> None: ...

    def test_isCoreInverted(self) -> None:
        inverted = motorlib.grains.ConicalGrain()
        inverted.setProperties(
            {
                "length": 0.1,
                "diameter": 0.01,
                "forwardCoreDiameter": 0.0025,
                "aftCoreDiameter": 0.002,
            }
        )
        regular = motorlib.grains.ConicalGrain()
        regular.setProperties(
            {
                "length": 0.1,
                "diameter": 0.01,
                "forwardCoreDiameter": 0.003,
                "aftCoreDiameter": 0.004,
            }
        )

        self.assertEqual(inverted.isCoreInverted(), True)
        self.assertEqual(regular.isCoreInverted(), False)

    def test_getFrustumInfo(self) -> None:
        unregressed = self.testGrain.getFrustumInfo(0)
        self.assertAlmostEqual(
            unregressed[0], self.testGrain.props["forwardCoreDiameter"].getValue()
        )
        self.assertAlmostEqual(
            unregressed[1], self.testGrain.props["aftCoreDiameter"].getValue()
        )
        self.assertAlmostEqual(
            unregressed[2], self.testGrain.props["length"].getValue()
        )

        beforeHittingWall = self.testGrain.getFrustumInfo(0.001)
        self.assertAlmostEqual(beforeHittingWall[0], 0.004499993750029296)
        self.assertAlmostEqual(beforeHittingWall[1], 0.003999993750029297)
        self.assertAlmostEqual(
            beforeHittingWall[2], self.testGrain.props["length"].getValue()
        )  # Length hasn't changed yet

        hitWall = self.testGrain.getFrustumInfo(0.0038)
        self.assertAlmostEqual(
            hitWall[0], self.testGrain.props["diameter"].getValue()
        )  # This end has burned all the way to the wall
        self.assertAlmostEqual(hitWall[1], 0.009599976250111327)
        self.assertAlmostEqual(hitWall[2], 0.08000474997773462)

    def test_getSurfaceAreaAtRegression(self) -> None:

        forwardFaceArea = 7.36310778e-05
        aftFaceArea = 7.53982236e-05
        lateralArea = 0.00070686055598659

        self.assertAlmostEqual(
            self.testGrain.getSurfaceAreaAtRegression(0), lateralArea
        )
        self.assertAlmostEqual(
            self.testGrain.getSurfaceAreaAtRegression(0.001), 0.0013351790867045452
        )

        # For when uninibited conical grains work:
        self.testGrain.setProperty("inhibitedEnds", "Top")
        self.assertAlmostEqual(
            self.testGrain.getSurfaceAreaAtRegression(0), lateralArea + aftFaceArea
        )

        self.testGrain.setProperty("inhibitedEnds", "Bottom")
        self.assertAlmostEqual(
            self.testGrain.getSurfaceAreaAtRegression(0), lateralArea + forwardFaceArea
        )

        self.testGrain.setProperty("inhibitedEnds", "Neither")
        self.assertAlmostEqual(
            self.testGrain.getSurfaceAreaAtRegression(0),
            lateralArea + forwardFaceArea + aftFaceArea,
        )

    def test_getVolumeAtRegression(self) -> None:
        self.assertAlmostEqual(
            self.testGrain.getVolumeAtRegression(0), 7.454737567580781e-06
        )
        self.assertAlmostEqual(
            self.testGrain.getVolumeAtRegression(0.001), 6.433724127569215e-06
        )
        self.assertAlmostEqual(
            self.testGrain.getVolumeAtRegression(0.0038), 2.480054353678591e-07
        )

    def test_getWebLeft(self) -> None:
        self.assertAlmostEqual(self.testGrain.getWebLeft(0), 0.004)
        self.assertAlmostEqual(self.testGrain.getWebLeft(0.001), 0.003)
        self.assertAlmostEqual(self.testGrain.getWebLeft(0.0038), 0.0002)

        self.testGrain.setProperty("forwardCoreDiameter", 0.002)
        self.testGrain.setProperty("aftCoreDiameter", 0.0025)
        self.assertAlmostEqual(self.testGrain.getWebLeft(0), 0.004)
        self.assertAlmostEqual(self.testGrain.getWebLeft(0.001), 0.003)
        self.assertAlmostEqual(self.testGrain.getWebLeft(0.0038), 0.0002)


if __name__ == "__main__":
    unittest.main()
