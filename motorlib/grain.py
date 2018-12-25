from . import geometry

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

class grainProperty():
	def __init__(self, dispName, valueType):
		self.dispName = dispName
		self.valueType = valueType
		self.value = None

	def setValue(self, value):
		self.value = self.valueType(value)

	def getValue(self):
		return self.value

class floatGrainProperty(grainProperty):
	def __init__(self, dispName, minValue, maxValue):
		super().__init__(dispName, float)
		self.min = minValue
		self.max = maxValue

	def setValue(self, value):
		if value > self.min and value < self.max:
			super().setValue(value)

class intGrainProperty(grainProperty):
	def __init__(self, dispName, minValue, maxValue):
		super().__init__(dispName, int)
		self.min = minValue
		self.max = maxValue

	def setValue(self, value):
		if value > self.min and value < self.max:
			super().setValue(value)

class propellantGrainProperty(grainProperty):
	def __init__(self, dispName):
		super().__init__(dispName, dict)
		#self.proplist = proplist
		self.value = {'density': None, 'a': None, 'n': None, 'k': None, 't': None, 'm':None}

	def setValue(self, value):
		#TODO: check for proper properties
		self.value = value

class grain():
	def __init__(self):
		self.props = {
			'diameter': floatGrainProperty('Diameter', 0, 100),
			'length': floatGrainProperty('Length', 0, 100),
			'prop': propellantGrainProperty('Propellant')
		}

	def setProperties(self, props):
		for p in props.keys():
			self.props[p].setValue(props[p])

	def getProperties(self, props = None):
		if props is None:
			props = self.props.keys()
		return {k:self.props[k].getValue() for k in props}

	def getVolumeSlice(self, r, dR):
		return self.getVolumeAtRegression(r) - self.getVolumeAtRegression(r + dR)

	def getSurfaceAreaAtRegression(self, r):
		return None
	
	def getVolumeAtRegression(self, r):
		return None

	def getWebLeft(self, r):
		return None

	def isWebLeft(self, r):
		return self.getWebLeft(0) < 10000 * self.getWebLeft(r)

class batesGrain(grain):
	def __init__(self):
		super().__init__()
		self.props['coreDiameter'] = floatGrainProperty('Core Diameter', 0, 100)

	def getSurfaceAreaAtRegression(self, r):
		bLength = self.props['length'].getValue() - (r * 2)
		bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
		diameter = self.props['diameter'].getValue()

		faceArea = geometry.circleArea(diameter) - geometry.circleArea(bCoreDiameter)
		tubeArea = geometry.tubeArea(bCoreDiameter, bLength)

		return tubeArea + (2 * faceArea)

	def getVolumeAtRegression(self, r):
		bLength = self.props['length'].getValue() - (r * 2)
		bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
		diameter = self.props['diameter'].getValue()

		grainVol = geometry.cylinderVolume(diameter, bLength)
		coreVol = geometry.cylinderVolume(bCoreDiameter, bLength)

		return grainVol - coreVol

	def getWebLeft(self, r):
		return self.props['diameter'].getValue() - self.props['coreDiameter'].getValue() - (2 * r)
