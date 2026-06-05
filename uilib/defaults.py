"""Provides default properties for the UI."""

DEFAULT_PREFERENCES = {
    'general': {
        'maxPressure': 1500 * 6895,
        'maxMassFlux': 2 / 0.001422,
        'maxMachNumber': 0.7,
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
        'm': 'in',
        'm^3': 'in^3',
        'm/s': 'ft/s',
        'Pa': 'psi',
        'kg': 'lb',
        'kg/m^3': 'lb/in^3',
        'kg/s': 'lb/s',
        'kg/(m^2*s)': 'lb/(in^2*s)',
        '(m*Pa)/s': '(in*psi)/s',
        'm/(s*Pa)': 'thou/(s*psi)',
        'm/(s*Pa^n)': 'in/(s*psi^n)'
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

REDLINE_PROPS = {
            'name': 'RCS - Redline',
            'density': 1750,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 1.25e-05,
                    'n': 0.42,
                    't': 2550.0,
                    'm': 25.8,
                    'k': 1.24
                }
            ]
}
BLACK_MAX_PROPS = {
            'name': 'RCS - Black Max',
            'density': 1680,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 2.27e-05,
                    'n': 0.38,
                    't': 2750.0,
                    'm': 24.5,
                    'k': 1.22
                }
            ]
}
WARP_9_PROPS = {
            'name': 'RCS - Warp-9',
            'density': 1780,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 1.05e-05,
                    'n': 0.44,
                    't': 2400.0,
                    'm': 26.0,
                    'k': 1.24
                }
            ]
}
MOJAVE_GREEN_PROPS = {
            'name': 'RCS - Mojave Green',
            'density': 1700,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 3.85e-05,
                    'n': 0.35,
                    't': 2200.0,
                    'm': 27.5,
                    'k': 1.25
                }
            ]
}
CLASSIC_PROPS = {
            'name': 'RCS - Classic',
            'density': 1760,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 8.5e-06,
                    'n': 0.43,
                    't': 2450.0,
                    'm': 26.5,
                    'k': 1.24
                }
            ]
}
KNER_PROPS = {
            'name': 'Nakka - KNER',
            'density': 1820,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 2.9e-05,
                    'n': 0.40,
                    't': 1580.0,
                    'm': 42.0,
                    'k': 1.13
                }
            ]
}
AP_HTPB_8020_PROPS = {
            'name': 'AP/HTPB 80/20 (fine AP)',
            'density': 1720,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 2.75e-05,
                    'n': 0.35,
                    't': 2580.0,
                    'm': 25.0,
                    'k': 1.24
                }
            ]
}
AP_HTPB_AL_PROPS = {
            'name': 'AP/HTPB/Al 68/14/18',
            'density': 1780,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 1.85e-05,
                    'n': 0.40,
                    't': 3200.0,
                    'm': 28.0,
                    'k': 1.17
                }
            ]
}
AP_PBAN_AL_PROPS = {
            'name': 'AP/PBAN/Al (Space Shuttle SRB type)',
            'density': 1770,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 5.606e-06,
                    'n': 0.45,
                    't': 3450.0,
                    'm': 28.3,
                    'k': 1.16
                }
            ]
}
AEROTECH_FAST_PROPS = {
            'name': 'Aerotech-type Fast AP/HTPB',
            'density': 1700,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 5.0e-05,
                    'n': 0.34,
                    't': 2500.0,
                    'm': 25.5,
                    'k': 1.24
                }
            ]
}
AEROTECH_SLOW_PROPS = {
            'name': 'Aerotech-type Slow AP/HTPB',
            'density': 1750,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 5.5e-06,
                    'n': 0.45,
                    't': 2350.0,
                    'm': 27.0,
                    'k': 1.24
                }
            ]
}
AN_HTPB_PROPS = {
            'name': 'AN/HTPB (Ammonium Nitrate)',
            'density': 1550,
            'tabs': [
                {
                    'minPressure': 0.0,
                    'maxPressure': 10342500,
                    'a': 1.5e-05,
                    'n': 0.40,
                    't': 1600.0,
                    'm': 20.0,
                    'k': 1.28
                }
            ]
}

DEFAULT_PROPELLANTS = [
    CL_PROPS,
    OW_PROPS,
    KNDX_PROPS,
    KNSB_PROPS,
    KNSU_PROPS,
    WL_PROPS,
    BT_PROPS,
    REDLINE_PROPS,
    BLACK_MAX_PROPS,
    WARP_9_PROPS,
    MOJAVE_GREEN_PROPS,
    CLASSIC_PROPS,
    KNER_PROPS,
    AP_HTPB_8020_PROPS,
    AP_HTPB_AL_PROPS,
    AP_PBAN_AL_PROPS,
    AEROTECH_FAST_PROPS,
    AEROTECH_SLOW_PROPS,
    AN_HTPB_PROPS
]
