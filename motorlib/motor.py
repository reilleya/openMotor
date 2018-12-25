from . import grain
from . import geometry

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
