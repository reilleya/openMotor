import geometry

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

class motor():
	def __init__(self):
		self.grains = []
		self.nozzle = 0

	def calcKN(self, r):
		surfArea = sum([gr.getSurfaceAreaAtRegression(r) for gr in self.grains])
		nozz = geometry.circleArea(self.nozzle)
		return surfArea / nozz

	def calcIdealPressure(self, r):
		k = self.grains[0].props['prop'].getValue()['k']
		t0 = self.grains[0].props['prop'].getValue()['t']
		m = self.grains[0].props['prop'].getValue()['m']
		p = self.grains[0].props['prop'].getValue()['density']
		a = self.grains[0].props['prop'].getValue()['a']
		n = self.grains[0].props['prop'].getValue()['n']
		num = self.calcKN(r) * p * a
		denom = ((k/((8314/m)*t0))*((2/(k+1))**((k+1)/(k-1))))**0.5
		return (num/denom) ** (1/(1-n))

tm = motor()

bg = batesGrain()
print(bg.getProperties())
bg.setProperties({'diameter':0.083058, 
				  'length':0.1397, 
				  'coreDiameter':0.03175, 
				  'prop':{
				  	'density': 1685, 
				  	'a': 0.0000378476, 
				  	'n': 0.32, 
				  	't':1800, 
				  	'm':23.67, 
				  	'k':1.25}})
print(bg.getProperties())

tm.grains.append(bg)
tm.nozzle = 0.0102616

print(tm.grains[0].getVolumeAtRegression(0) * 1685)
print(tm.calcKN(0))
print(tm.calcIdealPressure(0)/6895)

reg = 0

p = [0, tm.calcIdealPressure(0)]
t = [0, 0.01]

ts = 0.01

while bg.getWebLeft(reg) > 0.00001:
	#print(t[-1])
	reg += ts*bg.props['prop'].getValue()['a'] * (p[-1]**bg.props['prop'].getValue()['n'])
	#print(reg)
	t.append(t[-1] + ts)
	p.append(tm.calcIdealPressure(reg))

t.append(t[-1] + ts)
p.append(0)

plt.plot(t, [pr/6895 for pr in p])
plt.show()
