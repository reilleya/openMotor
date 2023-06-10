"""Provides default properties for the UI."""
from motorlib.enums.units.BurnRateCoefficientUnit import BurnRateCoefficientUnit
from motorlib.enums.units.DensityUnit import DensityUnit
from motorlib.enums.units.LengthUnit import LengthUnit
from motorlib.enums.units.MassFlowUnit import MassFlowUnit
from motorlib.enums.units.MassFluxUnit import MassFluxUnit
from motorlib.enums.units.MassUnit import MassUnit
from motorlib.enums.units.NozzleErosionCoefficientUnit import NozzleErosionCoefficientUnit
from motorlib.enums.units.NozzleSlagCoefficientUnit import NozzleSlagCoefficientUnit
from motorlib.enums.units.PressureUnit import PressureUnit
from motorlib.enums.units.VelocityUnit import VelocityUnit
from motorlib.enums.units.VolumeUnit import VolumeUnit

DEFAULT_PREFERENCES = {
    'general': {
        'maxPressure': 1500 * 6895,
        'maxMassFlux': 2 / 0.001422,
        'minPortThroat': 2,
        'burnoutWebThres': 0.001 / 39.37,
        'burnoutThrustThres': 0.1,
        'timestep': 0.03,
        'ambPressure': 101325,
        'igniterPressure': 150 * 6895, # Deprecated, but needed for migration
        'mapDim': 750,
        'sepPressureRatio' : 0.4, # This is a good default value known as the Summerfield Criteria https://ntrs.nasa.gov/api/citations/19840011402/downloads/19840011402.pdf
        'flowSeparationWarnPercent': 0.05
    },
    'units': {
        LengthUnit.METER: LengthUnit.INCH,
        VolumeUnit.CUBIC_METER: VolumeUnit.CUBIC_INCH,
        VelocityUnit.METER_PER_SECOND: VelocityUnit.FOOT_PER_SECOND,
        PressureUnit.PASCAL: PressureUnit.POUND_PER_SQUARE_INCH,
        MassUnit.KILOGRAM: MassUnit.POUND,
        DensityUnit.KILOGRAM_PER_CUBIC_METER: DensityUnit.POUND_PER_CUBIC_INCH,
        MassFlowUnit.KILOGRAM_PER_SECOND:MassFlowUnit.POUND_PER_SECOND,
        MassFluxUnit.KILOGRAM_PER_SQUARE_METER_PER_SECOND: MassFluxUnit.POUND_PER_SQUARE_INCH_PER_SECOND,
        NozzleSlagCoefficientUnit.METER_PASCAL_PER_SECOND: NozzleSlagCoefficientUnit.INCH_POUND_PER_SQUARE_INCH_PER_SECOND,
        NozzleErosionCoefficientUnit.METER_PER_SECOND_PASCAL: NozzleErosionCoefficientUnit.THOUSANDTH_INCH_PER_SECOND_POUND_PER_SQUARE_INCH,
        BurnRateCoefficientUnit.METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N: BurnRateCoefficientUnit.INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N
    }
}

CL_PROPS = {
            'name': 'MIT - Cherry Limeade',
            'density': 1670,
            'tabs': [
                {
                    'minPressure': 0,
                    'maxPressure': 6.895e+06,
                    'a': 3.517054143255937e-05,
                    'n': 0.3273,
                    't': 2800,
                    'm': 23.67,
                    'k': 1.21
                }
            ]
}
OW_PROPS = {
            'name': 'MIT - Ocean Water',
            'density': 1650,
            'tabs': [
                {
                    'minPressure': 0,
                    'maxPressure': 6.895e+06,
                    'a': 1.467e-05,
                    'n': 0.382,
                    't': 2600,
                    'm': 23.67,
                    'k': 1.25
                }
            ]
}
KNDX_PROPS = {
            'name': 'Nakka - KNDX',
            'density': 1785,
            'tabs': [
                {
                    'minPressure': 103425,
                    'maxPressure': 779135,
                    'a': 1.7096289148678155e-06,
                    'n': 0.619,
                    't': 1625.0,
                    'm': 42.39,
                    'k': 1.1308
                },
                {
                    'minPressure': 779135,
                    'maxPressure': 2571835,
                    'a': 0.008553459092346196,
                    'n': -0.009,
                    't': 1625.0,
                    'm': 42.39,
                    'k': 1.1308
                },
                {
                    'minPressure': 2571835,
                    'maxPressure': 5929700,
                    'a': 2.90330733578913e-07,
                    'n': 0.688,
                    't': 1625.0,
                    'm': 42.39,
                    'k': 1.1308
                },
                {
                    'minPressure': 5929700,
                    'maxPressure': 8501535,
                    'a': 0.1330457207587796,
                    'n': -0.148,
                    't': 1625.0,
                    'm': 42.39,
                    'k': 1.1308
                },
                {
                    'minPressure': 8501535,
                    'maxPressure': 11204375,
                    'a': 1.0537671694797537e-05,
                    'n': 0.444,
                    't': 1625.0,
                    'm': 42.39,
                    'k': 1.1308
                }
            ]
}
KNSB_PROPS = {
            'name': 'Nakka - KNSB',
            'density': 1750,
            'tabs': [
                {
                    'minPressure': 103425,
                    'maxPressure': 806715,
                    'a': 1.9253259619746373e-06,
                    'n': 0.625,
                    't': 1520.0,
                    'm': 39.9,
                    'k': 1.1361
                },
                {
                    'minPressure': 806715,
                    'maxPressure': 1503110,
                    'a': 0.6656608561590813,
                    'n': -0.313,
                    't': 1520.0,
                    'm': 39.9,
                    'k': 1.1361
                },
                {
                    'minPressure': 1503110,
                    'maxPressure': 3792250,
                    'a': 0.009528121181782798,
                    'n': -0.0145,
                    't': 1520.0,
                    'm': 39.9,
                    'k': 1.1361
                },
                {
                    'minPressure': 3792250,
                    'maxPressure': 7032900,
                    'a': 2.709667768835332e-06,
                    'n': 0.5245,
                    't': 1520.0,
                    'm': 39.9,
                    'k': 1.1361
                },
                {
                    'minPressure': 7032900,
                    'maxPressure': 10673460,
                    'a': 0.00417677261069904,
                    'n': 0.059,
                    't': 1520.0,
                    'm': 39.9,
                    'k': 1.1361
                }
            ]
}
WL_PROPS = {
            'name': 'RCS - White Lightning',
            'density': 1820.230130676801,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 5.710516747228669e-06,
                    'n': 0.45,
                    't': 2339.0,
                    'm': 27.125,
                    'k': 1.243
                }
            ]
}
BT_PROPS = {
            'name': 'RCS - Blue Thunder',
            'density': 1625.0868456817973,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 6.994600946367753e-05,
                    'n': 0.321,
                    't': 2616.5,
                    'm': 22.959,
                    'k': 1.235
                }
            ]
}
KNSU_PROPS = {
            'name': 'Nakka - KNSU',
            'density': 1800,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 0.00010073115141607291,
                    'n': 0.319,
                    't': 1720,
                    'm': 41.98,
                    'k': 1.133
                }
            ]
}

DEFAULT_PROPELLANTS = [CL_PROPS, OW_PROPS, KNDX_PROPS, KNSB_PROPS, KNSU_PROPS, WL_PROPS, BT_PROPS]
