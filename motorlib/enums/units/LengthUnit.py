from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class LengthUnit(str, Enum):
    METER = 'm'
    CENTIMETER = 'cm'
    MILLIMETER = 'mm'
    INCH = 'in'
    FOOT = 'ft'
