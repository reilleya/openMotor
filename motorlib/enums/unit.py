from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class Unit(str, Enum):
    # Angle
    DEGREES = 'deg'

    # Burn Rate Coefficient
    METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N = 'm/(s*Pa^n)'
    INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N = 'in/(s*psi^n)'

    # Density
    KILOGRAM_PER_CUBIC_METER = 'kg/m^3'
    POUND_PER_CUBIC_INCH = 'lb/in^3'
    GRAM_PER_CUBIC_CENTIMETER = 'g/cm^3'

    # Force
    NEWTON = 'N'
    POUND_FORCE = 'lbf'

    # Impulse
    NEWTON_SECOND = 'Ns'
    POUND_FORCE_SECOND = 'lbfs'

    # Length
    METER = 'm'
    CENTIMETER = 'cm'
    MILLIMETER = 'mm'
    INCH = 'in'
    FOOT = 'ft'

    # Mass Flow
    KILOGRAM_PER_SECOND = 'kg/s'
    POUND_PER_SECOND = 'lb/s'
    GRAM_PER_SECOND = 'g/s'

    # Mass Flux
    KILOGRAM_PER_SQUARE_METER_PER_SECOND = 'kg/(m^2*s)'
    POUND_PER_SQUARE_INCH_PER_SECOND = 'lb/(in^2*s)'

    # Mass
    KILOGRAM = 'kg'
    GRAM = 'g'
    POUND = 'lb'
    OUNCE = 'oz'
    GRAM_PER_MOLE = 'g/mol'

    # Nozzle Erosion Coefficient
    METER_PER_SECOND_PASCAL = 'm/(s*Pa)'
    METER_PER_SECOND_MEGAPASCAL = 'm/(s*MPa)'
    THOUSANDTH_INCH_PER_SECOND_POUND_PER_SQUARE_INCH = 'thou/(s*psi)'

    # Nozzle Slag Coefficient
    METER_PASCAL_PER_SECOND = '(m*Pa)/s'
    METER_MEGAPASCAL_PER_SECOND = '(m*MPa)/s'
    INCH_POUND_PER_SQUARE_INCH_PER_SECOND = '(in*psi)/s'

    # Pressure
    PASCAL = 'Pa'
    MEGAPASCAL = 'MPa'
    POUND_PER_SQUARE_INCH = 'psi'

    # Temperature
    KELVIN = 'K'

    # Time
    SECOND = 's'

    # Velocity
    METER_PER_SECOND = 'm/s'
    CENTIMETER_PER_SECOND = 'cm/s'
    MILLIMETER_PER_SECOND = 'mm/s'
    FOOT_PER_SECOND = 'ft/s'
    INCH_PER_SECOND = 'in/s'

    # Volume
    CUBIC_METER = 'm^3'
    CUBIC_CENTIMETER = 'cm^3'
    CUBIC_MILLIMETER = 'mm^3'
    CUBIC_INCH = 'in^3'
    CUBIC_FOOT = 'ft^3'