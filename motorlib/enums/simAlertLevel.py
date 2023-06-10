from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class SimAlertLevel(str, Enum):
    """Levels of severity for sim alerts"""
    ERROR = 'Error'
    WARNING = 'Warning'
    MESSAGE = 'Message'
