from . import grain
from . import geometry

class motor():
	def __init__(self):
		self.grains = []
		self.nozzle = 0

	def calcKN(self, r):
		surfArea = sum([gr.getSurfaceAreaAtRegression(reg) * int(gr.isWebLeft(reg)) for gr, reg in zip(self.grains, r)])
		nozz = geometry.circleArea(self.nozzle)
		return surfArea / nozz

	def calcIdealPressure(self, r):
		k = self.grains[0].props['prop'].getValue()['k']
		t = self.grains[0].props['prop'].getValue()['t']
		m = self.grains[0].props['prop'].getValue()['m']
		p = self.grains[0].props['prop'].getValue()['density']
		a = self.grains[0].props['prop'].getValue()['a']
		n = self.grains[0].props['prop'].getValue()['n']
		num = self.calcKN(r) * p * a
		denom = ((k/((8314/m)*t))*((2/(k+1))**((k+1)/(k-1))))**0.5
		return (num/denom) ** (1/(1-n))

	def runSimulation(self):
		burnoutThres = 0.00001
		ts = 0.01

		perGrainReg = [0 for grain in self.grains]
		print(perGrainReg)

		p = [0, self.calcIdealPressure(perGrainReg)]
		k = [0, self.calcKN(perGrainReg)]
		t = [0, ts]

		while any([g.getWebLeft(r) > burnoutThres for g,r in zip(self.grains, perGrainReg)]):
			for gid, grain in enumerate(self.grains):
				if grain.getWebLeft(perGrainReg[gid]) > burnoutThres:
					perGrainReg[gid] += ts * grain.props['prop'].getValue()['a'] * (p[-1]**grain.props['prop'].getValue()['n'])

			#print(reg)
			t.append(t[-1] + ts)
			k.append(self.calcKN(perGrainReg))
			p.append(self.calcIdealPressure(perGrainReg))

		t.append(t[-1] + ts)
		k.append(0)
		p.append(0)

		return (t, k, p)