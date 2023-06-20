"""This module contains tables of units and their long form names, their conversion rates with other units, and
functions for performing conversion."""
from motorlib.enums.unit import Unit

# The keys in this dictionary specify the units that all calculations are done in internally
unitLabels = {
    Unit.METER: 'Length',
    Unit.CUBIC_METER: 'Volume',
    Unit.METER_PER_SECOND: 'Velocity',
    Unit.NEWTON: 'Force',
    Unit.NEWTON_SECOND: 'Impulse',
    Unit.PASCAL: 'Pressure',
    Unit.KILOGRAM: 'Mass',
    Unit.KILOGRAM_PER_CUBIC_METER: 'Density',
    Unit.KILOGRAM_PER_SECOND: 'Mass Flow',
    Unit.KILOGRAM_PER_SQUARE_METER_PER_SECOND: 'Mass Flux',
    Unit.METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N: 'Burn Rate Coefficient',
    Unit.METER_PASCAL_PER_SECOND: 'Nozzle Slag Coefficient',
    Unit.METER_PER_SECOND_PASCAL: 'Nozzle Erosion Coefficient'
}

unitTable = [
    (Unit.METER, Unit.CENTIMETER, 100),
    (Unit.METER, Unit.METER, 1000),
    (Unit.METER, Unit.INCH, 39.37),
    (Unit.METER, Unit.FOOT, 3.28),

    (Unit.CUBIC_METER, Unit.CUBIC_CENTIMETER, 100 ** 3),
    (Unit.CUBIC_METER, Unit.CUBIC_MILLIMETER, 1000 ** 3),
    (Unit.CUBIC_METER, Unit.CUBIC_INCH, 39.37 ** 3),
    (Unit.CUBIC_METER, Unit.CUBIC_FOOT, 3.28 ** 3),

    (Unit.METER_PER_SECOND, Unit.CENTIMETER_PER_SECOND, 100),
    (Unit.METER_PER_SECOND, Unit.MILLIMETER_PER_SECOND, 1000),
    (Unit.METER_PER_SECOND, Unit.FOOT_PER_SECOND, 3.28),
    (Unit.METER_PER_SECOND, Unit.INCH_PER_SECOND, 39.37),

    (Unit.NEWTON, Unit.POUND_FORCE, 0.2248),

    (Unit.NEWTON_SECOND, Unit.POUND_FORCE_SECOND, 0.2248),

    (Unit.PASCAL, Unit.MEGAPASCAL, 1 / 1000000),
    (Unit.PASCAL, Unit.POUND_PER_SQUARE_INCH, 1 / 6895),

    (Unit.KILOGRAM, Unit.GRAM, 1000),
    (Unit.KILOGRAM, Unit.POUND, 2.205),
    (Unit.KILOGRAM, Unit.OUNCE, 2.205 * 16),

    (Unit.KILOGRAM_PER_CUBIC_METER, Unit.POUND_PER_CUBIC_INCH, 3.61273e-5),
    (Unit.KILOGRAM_PER_CUBIC_METER, Unit.GRAM_PER_CUBIC_CENTIMETER, 0.001),

    (Unit.KILOGRAM_PER_SECOND, Unit.POUND_PER_SECOND, 2.205),
    (Unit.KILOGRAM_PER_SECOND, Unit.GRAM_PER_SECOND, 1000),

    (Unit.KILOGRAM_PER_SQUARE_METER_PER_SECOND, Unit.POUND_PER_SQUARE_INCH_PER_SECOND, 0.001422),

    (Unit.METER_PASCAL_PER_SECOND, Unit.METER_MEGAPASCAL_PER_SECOND, 1000000),
    (Unit.METER_PASCAL_PER_SECOND, Unit.INCH_POUND_PER_SQUARE_INCH_PER_SECOND,
     0.00571014715),

    (Unit.METER_PER_SECOND_PASCAL, Unit.METER_PER_SECOND_MEGAPASCAL,
     1 / 1000000),
    (Unit.METER_PER_SECOND_PASCAL,
     Unit.THOUSANDTH_INCH_PER_SECOND_POUND_PER_SQUARE_INCH, 271447138),

    (Unit.METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N,
     Unit.INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N, 39.37)
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
