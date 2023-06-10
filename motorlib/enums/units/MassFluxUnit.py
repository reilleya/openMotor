from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class MassFluxUnit(str, Enum):
    KILOGRAM_PER_SQUARE_METER_PER_SECOND = 'kg/(m^2*s)'
    POUND_PER_SQUARE_INCH_PER_SECOND = 'lb/(in^2*s)'
