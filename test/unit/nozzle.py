import unittest
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

if __name__ == '__main__':
    unittest.main()
