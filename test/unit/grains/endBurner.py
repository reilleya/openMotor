import unittest
import motorlib.grains

class EndBurningGrainMethods(unittest.TestCase):

    def test_getSurfaceAreaAtRegression(self):
        grain = motorlib.grains.EndBurningGrain()
        grain.setProperties({
            'length': 0.1,
            'diameter': 0.01,
        })
        self.assertAlmostEqual(grain.getSurfaceAreaAtRegression(0), 7.853981633974483e-05)
        self.assertAlmostEqual(grain.getSurfaceAreaAtRegression(0.05), 7.853981633974483e-05)
        grain.setProperties({
            'length': 0.1,
            'diameter': 0.02,
        })
        self.assertAlmostEqual(grain.getSurfaceAreaAtRegression(0), 0.0003141592653589793)
        self.assertAlmostEqual(grain.getSurfaceAreaAtRegression(0.05), 0.0003141592653589793)

    def test_getVolumeAtRegression(self):
        grain = motorlib.grains.EndBurningGrain()
        grain.setProperties({
            'length': 0.1,
            'diameter': 0.01,
        })
        self.assertAlmostEqual(grain.getVolumeAtRegression(0), 7.853981633974484e-06)
        self.assertAlmostEqual(grain.getVolumeAtRegression(0.05), 3.926990816987242e-06)
        grain.setProperties({
            'length': 0.2,
            'diameter': 0.02,
        })
        self.assertAlmostEqual(grain.getVolumeAtRegression(0), 6.283185307179587e-05)
        self.assertAlmostEqual(grain.getVolumeAtRegression(0.05), 4.7123889803846906e-05)


    def test_getWebLeft(self):
        grain = motorlib.grains.EndBurningGrain()
        grain.setProperties({
            'length': 0.1,
            'diameter': 0.01,
        })
        self.assertAlmostEqual(grain.getWebLeft(0), 0.1)
        self.assertAlmostEqual(grain.getWebLeft(0.05), 0.1 - 0.05)
        grain.setProperties({
            'length': 0.2,
            'diameter': 0.01,
        })
        self.assertAlmostEqual(grain.getWebLeft(0), 0.2)
        self.assertAlmostEqual(grain.getWebLeft(0.07), 0.2 - 0.07)

    def test_getEndPositions(self):
        grain = motorlib.grains.EndBurningGrain()
        grain.setProperties({
            'length': 0.1,
            'diameter': 0.01,
        })
        self.assertAlmostEqual(grain.getEndPositions(0), (0, 0.1))
        self.assertAlmostEqual(grain.getEndPositions(0.05), (0, 0.1 - 0.05))
        grain.setProperties({
            'length': 0.2,
            'diameter': 0.01,
        })
        self.assertAlmostEqual(grain.getEndPositions(0), (0, 0.2))
        self.assertAlmostEqual(grain.getEndPositions(0.07), (0, 0.2 - 0.07))

if __name__ == '__main__':
    unittest.main()
