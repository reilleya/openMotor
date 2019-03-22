from enum import Enum

class simAlertLevel(Enum):
	ERROR = 1
	WARNING = 2
	MESSAGE = 3

class simAlertType(Enum):
	GEOMETRY = 1
	CONSTRAINT = 2

class simAlert():
	def __init__(self, level, alertType, description, location = None):
		self.level = level
		self.type = alertType
		self.description = description
		self.location = location
