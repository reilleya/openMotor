from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class DensityUnit(str, Enum):
    KILOGRAM_PER_CUBIC_METER = 'kg/m^3'
    POUND_PER_CUBIC_INCH = 'lb/in^3'
    GRAM_PER_CUBIC_CENTIMETER = 'g/cm^3'
