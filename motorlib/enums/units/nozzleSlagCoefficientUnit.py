from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class NozzleSlagCoefficientUnit(str, Enum):
    METER_PASCAL_PER_SECOND = '(m*Pa)/s'
    METER_MEGAPASCAL_PER_SECOND = '(m*MPa)/s'
    INCH_POUND_PER_SQUARE_INCH_PER_SECOND = '(in*psi)/s'

