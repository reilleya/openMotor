"""This module contains tables of units and their long form names, their conversion rates with other units, and
functions for performing conversion."""
from motorlib.enums.units.burnRateCoefficientUnit import BurnRateCoefficientUnit
from motorlib.enums.units.densityUnit import DensityUnit
from motorlib.enums.units.forceUnit import ForceUnit
from motorlib.enums.units.impulseUnit import ImpulseUnit
from motorlib.enums.units.lengthUnit import LengthUnit
from motorlib.enums.units.massFlowUnit import MassFlowUnit
from motorlib.enums.units.massFluxUnit import MassFluxUnit
from motorlib.enums.units.massUnit import MassUnit
from motorlib.enums.units.nozzleErosionCoefficientUnit import NozzleErosionCoefficientUnit
from motorlib.enums.units.nozzleSlagCoefficientUnit import NozzleSlagCoefficientUnit
from motorlib.enums.units.pressureUnit import PressureUnit
from motorlib.enums.units.velocityUnit import VelocityUnit
from motorlib.enums.units.volumeUnit import VolumeUnit

# The keys in this dictionary specify the units that all calculations are done in internally
unitLabels = {
    LengthUnit.METER: 'Length',
    VolumeUnit.CUBIC_METER: 'Volume',
    VelocityUnit.METER_PER_SECOND: 'Velocity',
    ForceUnit.NEWTON: 'Force',
    ImpulseUnit.NEWTON_SECOND: 'Impulse',
    PressureUnit.PASCAL: 'Pressure',
    MassUnit.KILOGRAM: 'Mass',
    DensityUnit.KILOGRAM_PER_CUBIC_METER: 'Density',
    MassFlowUnit.KILOGRAM_PER_SECOND: 'Mass Flow',
    MassFluxUnit.KILOGRAM_PER_SQUARE_METER_PER_SECOND: 'Mass Flux',
    BurnRateCoefficientUnit.METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N: 'Burn Rate Coefficient',
    NozzleSlagCoefficientUnit.METER_PASCAL_PER_SECOND: 'Nozzle Slag Coefficient',
    NozzleErosionCoefficientUnit.METER_PER_SECOND_PASCAL: 'Nozzle Erosion Coefficient'
}

unitTable = [
    (LengthUnit.METER, LengthUnit.CENTIMETER, 100),
    (LengthUnit.METER, LengthUnit.METER, 1000),
    (LengthUnit.METER, LengthUnit.INCH, 39.37),
    (LengthUnit.METER, LengthUnit.FOOT, 3.28),

    (VolumeUnit.CUBIC_METER, VolumeUnit.CUBIC_CENTIMETER, 100 ** 3),
    (VolumeUnit.CUBIC_METER, VolumeUnit.CUBIC_MILLIMETER, 1000 ** 3),
    (VolumeUnit.CUBIC_METER, VolumeUnit.CUBIC_INCH, 39.37 ** 3),
    (VolumeUnit.CUBIC_METER, VolumeUnit.CUBIC_FOOT, 3.28 ** 3),

    (VelocityUnit.METER_PER_SECOND, VelocityUnit.CENTIMETER_PER_SECOND, 100),
    (VelocityUnit.METER_PER_SECOND, VelocityUnit.MILLIMETER_PER_SECOND, 1000),
    (VelocityUnit.METER_PER_SECOND, VelocityUnit.FOOT_PER_SECOND, 3.28),
    (VelocityUnit.METER_PER_SECOND, VelocityUnit.INCH_PER_SECOND, 39.37),

    (ForceUnit.NEWTON, ForceUnit.POUND_FORCE, 0.2248),

    (ImpulseUnit.NEWTON_SECOND, ImpulseUnit.POUND_FORCE_SECOND, 0.2248),

    (PressureUnit.PASCAL, PressureUnit.MEGAPASCAL, 1 / 1000000),
    (PressureUnit.PASCAL, PressureUnit.POUND_PER_SQUARE_INCH, 1 / 6895),

    (MassUnit.KILOGRAM, MassUnit.GRAM, 1000),
    (MassUnit.KILOGRAM, MassUnit.POUND, 2.205),
    (MassUnit.KILOGRAM, MassUnit.OUNCE, 2.205 * 16),

    (DensityUnit.KILOGRAM_PER_CUBIC_METER, DensityUnit.POUND_PER_CUBIC_INCH, 3.61273e-5),
    (DensityUnit.KILOGRAM_PER_CUBIC_METER, DensityUnit.GRAM_PER_CUBIC_CENTIMETER, 0.001),

    (MassFlowUnit.KILOGRAM_PER_SECOND, MassFlowUnit.POUND_PER_SECOND, 2.205),
    (MassFlowUnit.KILOGRAM_PER_SECOND, MassFlowUnit.GRAM_PER_SECOND, 1000),

    (MassFluxUnit.KILOGRAM_PER_SQUARE_METER_PER_SECOND, MassFluxUnit.POUND_PER_SQUARE_INCH_PER_SECOND, 0.001422),

    (NozzleSlagCoefficientUnit.METER_PASCAL_PER_SECOND, NozzleSlagCoefficientUnit.METER_MEGAPASCAL_PER_SECOND, 1000000),
    (NozzleSlagCoefficientUnit.METER_PASCAL_PER_SECOND, NozzleSlagCoefficientUnit.INCH_POUND_PER_SQUARE_INCH_PER_SECOND,
     0.00571014715),

    (NozzleErosionCoefficientUnit.METER_PER_SECOND_PASCAL, NozzleErosionCoefficientUnit.METER_PER_SECOND_MEGAPASCAL,
     1 / 1000000),
    (NozzleErosionCoefficientUnit.METER_PER_SECOND_PASCAL,
     NozzleErosionCoefficientUnit.THOUSANDTH_INCH_PER_SECOND_POUND_PER_SQUARE_INCH, 271447138),

    (BurnRateCoefficientUnit.METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N,
     BurnRateCoefficientUnit.INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N, 39.37)
    # Ratio converts m/s to in/s. The pressure conversion must be done separately
]


def getAllConversions(unit):
    """Returns a list of all units that the passed unit can be converted to."""
    allConversions = [unit]
    for conversion in unitTable:
        if conversion[0] == unit:
            allConversions.append(conversion[1])
        elif conversion[1] == unit:
            allConversions.append(conversion[0])
    return allConversions


def getConversion(originUnit, destUnit):
    """Returns the ratio to convert between the two units. If the conversion does not exist, an exception is raised."""
    if originUnit == destUnit:
        return 1
    for conversion in unitTable:
        if conversion[0] == originUnit and conversion[1] == destUnit:
            return conversion[2]
        if conversion[1] == originUnit and conversion[0] == destUnit:
            return 1 / conversion[2]
    raise KeyError("Cannot find conversion from <" + originUnit + "> to <" + destUnit + ">")


def convert(quantity, originUnit, destUnit):
    """Returns the value of 'quantity' when it is converted from 'originUnit' to 'destUnit'."""
    return quantity * getConversion(originUnit, destUnit)


def convertAll(quantities, originUnit, destUnit):
    """Converts a list of values from 'originUnit' to 'destUnit'."""
    convRate = getConversion(originUnit, destUnit)
    return [q * convRate for q in quantities]


def convFormat(quantity, originUnit, destUnit, places=3):
    """Takes in a quantity in originUnit, converts it to destUnit and outputs a rounded and formatted string that
    includes the unit appended to the end."""
    rounded = round(convert(quantity, originUnit, destUnit), places)
    return '{} {}'.format(rounded, destUnit)
