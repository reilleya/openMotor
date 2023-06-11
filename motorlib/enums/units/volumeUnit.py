from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class VolumeUnit(str, Enum):
    CUBIC_METER = 'm^3'
    CUBIC_CENTIMETER = 'cm^3'
    CUBIC_MILLIMETER = 'mm^3'
    CUBIC_INCH = 'in^3'
    CUBIC_FOOT = 'ft^3'
