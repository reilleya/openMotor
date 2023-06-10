from enum import Enum


class SimAlertType(Enum):
    """Types of sim alerts"""
    GEOMETRY = 1
    CONSTRAINT = 2
    VALUE = 3
