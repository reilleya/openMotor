from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class VelocityUnit(str, Enum):
    METER_PER_SECOND = 'm/s'
    CENTIMETER_PER_SECOND = 'cm/s'
    MILLIMETER_PER_SECOND = 'mm/s'
    FOOT_PER_SECOND = 'ft/s'
    INCH_PER_SECOND = 'in/s'
