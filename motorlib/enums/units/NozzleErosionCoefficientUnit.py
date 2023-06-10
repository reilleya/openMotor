from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class NozzleErosionCoefficientUnit(str, Enum):
    METER_PER_SECOND_PASCAL = 'm/(s*Pa)'
    METER_PER_SECOND_MEGAPASCAL = 'm/(s*MPa)'
    THOUSANDTH_INCH_PER_SECOND_POUND_PER_SQUARE_INCH = 'thou/(s*psi)'
