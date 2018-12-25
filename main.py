import motorlib

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

tm = motorlib.motor()

bg = motorlib.batesGrain()
bg.setProperties({'diameter':0.083058, 
				  'length':0.1397, 
				  'coreDiameter':0.03175, 
				  'prop':{
				  	'density': 1685, 
				  	'a': 0.0000378476, 
				  	'n': 0.32, 
				  	't': 1800, 
				  	'm': 23.67, 
				  	'k': 1.25}})

bg2 = motorlib.batesGrain()
bg2.setProperties({'diameter':0.083058, 
				  'length':0.1397, 
				  'coreDiameter':0.05, 
				  'prop':{
				  	'density': 1685, 
				  	'a': 0.0000378476, 
				  	'n': 0.32, 
				  	't': 1800, 
				  	'm': 23.67, 
				  	'k': 1.25}})

tm.grains.append(bg)
tm.grains.append(bg2)
tm.nozzle = 0.0102616

t, k, p = tm.runSimulation()
plt.plot(t, [pr/6895 for pr in p])
plt.plot(t, k)
plt.show()
