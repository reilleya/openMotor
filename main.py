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
                    'density': 1690, 
                    'a': 3.517054143255937e-05, 
                    'n': 0.3273, 
                    't': 2770, 
                    'm': 23.67, 
                    'k': 1.25}})

bg2 = motorlib.batesGrain()
bg2.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'prop':{
                    'density': 1690, 
                    'a': 3.517054143255937e-05, 
                    'n': 0.3273, 
                    't': 2770, 
                    'm': 23.67, 
                    'k': 1.25}})

bg3 = motorlib.batesGrain()
bg3.setProperties({'diameter':0.083058, 
                  'length':0.1397, 
                  'coreDiameter':0.05, 
                  'prop':{
                    'density': 1890, 
                    'a': 0.000101, 
                    'n': 0.319, 
                    't': 1720, 
                    'm': 41.98, 
                    'k': 1.133}})

tm.grains.append(bg)
#tm.grains.append(bg2)
#tm.grains.append(bg3)
tm.nozzle = 0.0102616
#tm.nozzle = 0.01428

print(tm.calcKN([0]))
print(tm.calcIdealPressure([0]))

t, k, p = tm.runSimulation()
plt.plot(t, [pr/6895 for pr in p])
plt.plot(t, k)
plt.show()
