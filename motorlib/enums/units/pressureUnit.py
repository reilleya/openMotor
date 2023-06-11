from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class PressureUnit(str, Enum):
    PASCAL = 'Pa'
    MEGAPASCAL = 'MPa'
    POUND_PER_SQUARE_INCH = 'psi'
