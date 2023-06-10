import unittest
import motorlib.grains
from motorlib.enums.simAlertLevel import SimAlertLevel
from motorlib.enums.simAlertType import SimAlertType


class BatesGrainMethods(unittest.TestCase):

    def test_getDetailsString(self):
        grain = motorlib.grains.BatesGrain()
        grain.setProperties({
            'length': 0.1,
            'diameter': 0.05,
            'coreDiameter': 0.02
        })
        self.assertEqual(grain.getDetailsString(), 'Length: 0.1 m, Core: 0.02 m')
        self.assertEqual(grain.getDetailsString('cm'), 'Length: 10 cm, Core: 2 cm')

    def test_getGeometryErrors(self):
        grain = motorlib.grains.BatesGrain()
        grain.setProperties({
            'length': 0.1,
            'diameter': 0.05,
            'coreDiameter': 0.02
        })
        self.assertEqual(grain.getGeometryErrors(), [])

        grain.setProperties({
            'length': 0.1,
            'diameter': 0.05,
            'coreDiameter': 0.0
        })
        errors = grain.getGeometryErrors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].level, SimAlertLevel.ERROR)
        self.assertEqual(errors[0].type, SimAlertType.GEOMETRY)
        self.assertEqual(errors[0].description, 'Core diameter must not be 0')

        grain.setProperties({
            'length': 0.1,
            'diameter': 0.05,
            'coreDiameter': 0.7
        })
        errors = grain.getGeometryErrors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].level, SimAlertLevel.ERROR)
        self.assertEqual(errors[0].type, SimAlertType.GEOMETRY)
        self.assertEqual(errors[0].description, 'Core diameter must be less than grain diameter')


if __name__ == '__main__':
    unittest.main()
