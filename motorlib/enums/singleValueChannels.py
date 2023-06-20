from enum import Enum


# Python 3.11 supports `StrEnum` that would make this a bit more concise to write
# https://docs.python.org/3/library/enum.html#enum.StrEnum
class SingleValueChannels(str, Enum):
    TIME = 'time'
    KN = 'kn'
    PRESSURE = 'pressure'
    FORCE = 'force'
    VOLUME_LOADING = 'volumeLoading'
    EXIT_PRESSURE = 'exitPressure'
    D_THROAT = 'dThroat'
