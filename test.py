import motorlib
import unittest

class TestMotorMethods(unittest.TestCase):

    def test_calcKN(self):

        tm = motorlib.motor()

        bg = motorlib.batesGrain()
        bg.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'inhibitedEnds':0
                  })

        tm.grains.append(bg)
        tm.nozzle.setProperties({'throat': 0.01428})

        self.assertAlmostEqual(tm.calcKN([0]), 180, 0)
        self.assertAlmostEqual(tm.calcKN([0.0025]), 183, 0)
        self.assertAlmostEqual(tm.calcKN([0.005]), 185, 0)


    def test_calcPressure(self):
        tm = motorlib.motor()

        bg = motorlib.batesGrain()
        bg.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'inhibitedEnds':0
                  })

        tm.grains.append(bg)

        tm.nozzle.setProperties({'throat': 0.01428})
        tm.propellant.setProperties({
                    'name': 'KNSU',
                    'density': 1890, 
                    'a': 0.000101, 
                    'n': 0.319, 
                    't': 1720, 
                    'm': 41.98, 
                    'k': 1.133})
        self.assertAlmostEqual(tm.calcIdealPressure([0]), 4050030, 0)


class TestGeometryMethods(unittest.TestCase):
    def test_circle(self):
        self.assertAlmostEqual(motorlib.circleArea(0.5), 0.19634954)

    def test_tubeArea(self):
        self.assertAlmostEqual(motorlib.tubeArea(0.5, 2), 3.14159265)

    def test_cylinderArea(self):
        self.assertAlmostEqual(motorlib.cylinderArea(0.5, 2), 3.53429174)

    def test_cylinderVolume(self):
        self.assertAlmostEqual(motorlib.cylinderVolume(0.5, 2), 0.39269908)

class TestNozzleMethods(unittest.TestCase):
    def test_expansionRatio(self):
        self.assertAlmostEqual(motorlib.eRatioFromPRatio(1.15, 0.0156), 0.10650602)

unittest.main()