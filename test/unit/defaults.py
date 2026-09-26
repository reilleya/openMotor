import unittest

from motorlib.units import unitLabels
from uilib.defaults import DEFAULT_PREFERENCES


class TestDefaults(unittest.TestCase):

    def test_default_display_units_are_si(self):
        units = DEFAULT_PREFERENCES['units']

        self.assertEqual(set(units), set(unitLabels))
        self.assertNotIn('in', units.values())
        self.assertNotIn('ft', units.values())
        self.assertNotIn('psi', units.values())
        self.assertNotIn('lb', units.values())
