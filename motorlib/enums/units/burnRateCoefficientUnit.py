from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class BurnRateCoefficientUnit(str, Enum):
    METER_PER_SECOND_PASCAL_TO_THE_POWER_OF_N = 'm/(s*Pa^n)'
    INCH_PER_SECOND_POUND_PER_SQUARE_INCH_TO_THE_POWER_OF_N = 'in/(s*psi^n)'

