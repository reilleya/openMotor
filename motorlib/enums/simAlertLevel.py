from enum import Enum


class SimAlertLevel(Enum):
    """Levels of severity for sim alerts"""
    ERROR = 1
    WARNING = 2
    MESSAGE = 3
