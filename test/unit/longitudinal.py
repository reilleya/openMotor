import unittest

import numpy as np

import motorlib.grains
import motorlib.motor
from motorlib.longitudinal import grain_profile


class LongitudinalSectionMethods(unittest.TestCase):

    def setUp(self):
        self.config = motorlib.motor.MotorConfig()

    def test_bates_is_rectangle_with_growing_port(self):
        grain = motorlib.grains.BatesGrain()
        grain.setProperties(
            {
                "diameter": 0.1,
                "length": 0.2,
                "coreDiameter": 0.04,
                "inhibitedEnds": "Both",
            }
        )
        grain.simulationSetup(self.config)
        x0, outer0, inner0 = grain_profile(grain, 0)
        x1, outer1, inner1 = grain_profile(grain, 0.01)
        np.testing.assert_allclose(x0, [0, 0.2])
        np.testing.assert_allclose(outer0, [0.05, 0.05])
        np.testing.assert_allclose(inner0, [0.02, 0.02])
        np.testing.assert_allclose(outer1, outer0)
        self.assertTrue(np.all(inner1 > inner0))

    def test_end_burner_is_shrinking_rectangle(self):
        grain = motorlib.grains.EndBurningGrain()
        grain.setProperties({"diameter": 0.1, "length": 0.2})
        grain.simulationSetup(self.config)
        x, outer, inner = grain_profile(grain, 0.03)
        np.testing.assert_allclose(x, [0, 0.17])
        np.testing.assert_allclose(outer, [0.05, 0.05])
        np.testing.assert_allclose(inner, [0, 0])

    def test_hemispherical_profiles_join_at_full_radius(self):
        top = motorlib.grains.TopHemisphericalGrain()
        top.setProperties({"diameter": 0.1, "portDiameter": 0.04})
        top.simulationSetup(self.config)
        bottom = motorlib.grains.BottomHemisphericalGrain()
        bottom.setProperties(
            {
                "diameter": 0.1,
                "portDiameter": 0.04,
                "outletDiameter": 0.01,
            }
        )
        bottom.simulationSetup(self.config)
        _, topOuter, _ = grain_profile(top, 0)
        bottomX, bottomOuter, bottomInner = grain_profile(bottom, 0)
        self.assertAlmostEqual(topOuter[-1], 0.05)
        self.assertAlmostEqual(bottomOuter[0], 0.05)
        self.assertLess(bottomX[-1], bottom.getProperty("length"))
        self.assertAlmostEqual(bottomOuter[-1], bottomInner[-1])


if __name__ == "__main__":
    unittest.main()
