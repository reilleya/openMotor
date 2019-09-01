"""Provides default properties for the UI."""

def defaultPreferencesDict():
    prefDict = {}
    prefDict['general'] = {
        'maxPressure': 1500 * 6895,
        'maxMassFlux': 2 / 0.001422,
        'minPortThroat': 2,
        'burnoutWebThres': 0.01 / 39.37,
        'burnoutThrustThres': 0.1,
        'timestep': 0.03,
        'ambPressure': 101325,
        'igniterPressure': 150 * 6895,
        'mapDim': 750
    }
    prefDict['units'] = {
        'm': 'in',
        'm/s': 'ft/s',
        'Pa': 'psi',
        'kg': 'lb',
        'kg/m^3': 'lb/in^3',
        'kg/s': 'lb/s',
        'kg/(m^2*s)': 'lb/(in^2*s)',
        'm/(s*Pa^n)': 'in/(s*psi^n)'
    }
    return prefDict

def defaultPropellants():
    clProps = {
                'name': 'MIT - Cherry Limeade',
                'density': 1680,
                'tabs': [
                    {
                        'minPressure': 0,
                        'maxPressure': 6.895e+06,
                        'a': 3.517054143255937e-05,
                        'n': 0.3273,
                        't': 3500,
                        'm': 23.67,
                        'k': 1.21
                    }
                ]
    }
    owProps = {
                'name': 'MIT - Ocean Water',
                'density': 1650,
                'tabs': [
                    {
                        'minPressure': 0,
                        'maxPressure': 6.895e+06,
                        'a': 1.467e-05,
                        'n': 0.382,
                        't': 3500,
                        'm': 23.67,
                        'k': 1.25
                    }
                ]
    }
    kndxProps = {
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
    knsbProps = {
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
    wlProps = {
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
    btProps = {
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
    return [clProps, owProps, kndxProps, knsbProps, wlProps, btProps]
