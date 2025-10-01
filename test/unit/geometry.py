import unittest

import motorlib.geometry


class TestGeometryMethods(unittest.TestCase):
    def test_circleArea(self) -> None:
        self.assertAlmostEqual(motorlib.geometry.circleArea(0.5), 0.19634954)

    def test_circlePerimeter(self) -> None:
        self.assertAlmostEqual(motorlib.geometry.circlePerimeter(0.5), 1.57079633)

    def test_circleDiameterFromArea(self) -> None:
        self.assertAlmostEqual(
            motorlib.geometry.circleDiameterFromArea(0.19634954), 0.5
        )

    def test_tubeArea(self) -> None:
        self.assertAlmostEqual(motorlib.geometry.tubeArea(0.5, 2), 3.14159265)

    def test_cylinderArea(self) -> None:
        self.assertAlmostEqual(motorlib.geometry.cylinderArea(0.5, 2), 3.53429174)

    def test_cylinderVolume(self) -> None:
        self.assertAlmostEqual(motorlib.geometry.cylinderVolume(0.5, 2), 0.39269908)

    def test_frustumLateralSurfaceArea(self) -> None:
        self.assertAlmostEqual(
            motorlib.geometry.frustumLateralSurfaceArea(2, 3, 5), 39.46576927
        )

    def test_frustumVolumeConeCase(self) -> None:
        self.assertAlmostEqual(motorlib.geometry.frustumVolume(0, 10, 10), 261.79938779)

    def test_frustumVolumeFrustumCase(self) -> None:
        self.assertAlmostEqual(
            motorlib.geometry.frustumVolume(10, 30, 50), 17016.96020694
        )

    def test_splitFrustumSimpleCase(self) -> None:
        self.assertEqual(
            motorlib.geometry.splitFrustum(1, 2, 4, 2), ((1, 1.5, 2), (1.5, 2, 2))
        )

    def test_splitFrustumInvertedCase(self) -> None:
        self.assertEqual(
            motorlib.geometry.splitFrustum(2, 1, 4, 2), ((2, 1.5, 2), (1.5, 1, 2))
        )

    def test_splitFrustum(self) -> None:
        """Make sure that the connected ends of the frustums line up"""
        upper, lower = motorlib.geometry.splitFrustum(1, 3, 3, 1)
        self.assertEqual(upper[1], lower[0])

    def test_dist_same_point(self) -> None:
        self.assertEqual(motorlib.geometry.dist((5, 5), (5, 5)), 0)

    def test_dist_horizontal_one_unit(self) -> None:
        self.assertEqual(motorlib.geometry.dist((5, 5), (6, 5)), 1)

    def test_dist_vertical_one_unit(self) -> None:
        self.assertEqual(motorlib.geometry.dist((5, 5), (5, 6)), 1)

    def test_dist_diagonal_negative_coords(self) -> None:
        expected_distance = 2**0.5  # sqrt(2)
        self.assertAlmostEqual(
            motorlib.geometry.dist((0, 0), (-1, -1)), expected_distance
        )


if __name__ == "__main__":
    unittest.main()
