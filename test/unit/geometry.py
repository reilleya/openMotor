import unittest
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

if __name__ == '__main__':
    unittest.main()
