import matplotlib
matplotlib.use('Qt4Agg')

import numpy as np
import pylab as plt
import skfmm
from skimage import measure

X, Y = np.meshgrid(np.linspace(-1,1,1001), np.linspace(-1,1,1001))
phi = np.ones_like(X)

# Moon burner
#phi[(X-0.5)**2 + Y**2 < 0.125] = 0

# Core
phi[X**2 + Y**2 < 0.175] = 0

# Fins
phi[np.logical_and(np.abs(Y)<0.125, np.abs(X)<0.7)] = 0
phi[np.logical_and(np.abs(X)<0.125, np.abs(Y)<0.7)] = 0
phi[np.logical_and(np.logical_and(X+Y<0.176, X+Y>-0.176), np.logical_and(X - 1 < Y, X + 1 > Y))] = 0
phi[np.logical_and(np.logical_and(X-Y<0.176, X-Y>-0.176), np.logical_and(-X - 1 < Y, -X + 1 > Y))] = 0

# Setup grain boundry (casting tube)
mask = X**2 + Y**2 > 1

phi  = np.ma.MaskedArray(phi, mask)
t    = skfmm.distance(phi, dx=1e-3)
plt.contour(X, Y, phi, [0], linewidths=(2), colors='black')
plt.contour(X, Y, phi.mask, [0], linewidths=(2), colors='red')
plt.contourf(X, Y, t, 20)
plt.show()

def length(contour):
    offset = np.roll(contour.T, 1, axis = 1)
    l = np.linalg.norm(contour.T - offset, axis = 0)
    return sum(list(l)[1:])

def clean(contour, m = 498):
    offset = np.array([[500, 500]])
    l = np.linalg.norm(contour - offset, axis = 1)
    return contour[l < m]

p = [0]

fig, ax = plt.subplots()

for i in range(0, 150, 3):
    contours = measure.find_contours(t, i/500, fully_connected='high')
    p.append(0)
    for n, contour in enumerate(contours):
        contour = clean(contour)
        p[-1] += length(contour)
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

ax.imshow(t, interpolation='nearest', cmap=plt.cm.gray)
plt.show()
plt.plot(p)
plt.show()
