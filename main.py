import motorlib

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

tm = motorlib.motor()

bg = motorlib.batesGrain()
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
