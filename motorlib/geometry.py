import math
import unittest

def circleArea(d):
    return ((d / 2) ** 2) * math.pi

def tubeArea(d, h):
    return d * math.pi * h

def cylinderArea(d, h):
    return (2 * circleArea(d)) + (tubeArea(d, h))

def cylinderVolume(d, h):
    return h * circleArea(d)

class TestGeometryMethods(unittest.TestCase):

    def test_circle(self):
        self.assertAlmostEqual(circleArea(0.5), 0.19634954)

    def test_tubeArea(self):
        self.assertAlmostEqual(tubeArea(0.5, 2), 3.14159265)

    def test_cylinderArea(self):
        self.assertAlmostEqual(cylinderArea(0.5, 2), 3.53429174)

    def test_cylinderVolume(self):
        self.assertAlmostEqual(cylinderVolume(0.5, 2), 0.39269908)

if __name__ == '__main__':
    unittest.main()
