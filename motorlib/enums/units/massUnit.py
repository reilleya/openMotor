from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class MassUnit(str, Enum):
    KILOGRAM = 'kg'
    GRAM = 'g'
    POUND = 'lb'
    OUNCE = 'oz'
    GRAM_PER_MOLE = 'g/mol'
