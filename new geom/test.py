import matplotlib
matplotlib.use('Qt4Agg')

import numpy as np
import pylab as plt
import skfmm
from skimage import measure

X, Y = np.meshgrid(np.linspace(-1,1,1001), np.linspace(-1,1,1001))
phi = np.ones_like(X)

# Bates

r = 0.39
phi[X**2 + Y**2 < r**2] = 0


# Moon burner
"""
offset = 0.55
r = 0.28
phi[(X-offset)**2 + Y**2 < r**2] = 0
"""

# Star grain
"""
w = 0.2
l = 0.5
n = 24
r = 0.025

for i in range(0, n):
    th = 2*np.pi/n * i
    a = np.cos(th)
    b = np.sin(th)

    vect = abs(a*X + b*Y) < w/2 * (1 - (((X**2 + Y**2) ** 0.5) / l))
    near = b*X - a*Y > -0.025
    phi[np.logical_and(vect, near)] = 0
"""

# X core
"""
w = 0.125
l = 0.7
phi[np.logical_and(np.abs(Y)<w/2, np.abs(X)<l)] = 0
phi[np.logical_and(np.abs(X)<w/2, np.abs(Y)<l)] = 0
"""

# C slot
"""
w = 0.125
offset = 0.5
phi[np.logical_and(np.abs(Y)<w/2, X>offset)] = 0
"""

# D grain
"""
offset = 0.5
phi[X>offset] = 0
"""

# Finocyl
"""
w = 0.1366
l = 0.272
n = 8
r = 0.39

phi[X**2 + Y**2 < r**2] = 0
l += r
for i in range(0, n):
    th = 2*np.pi/n * i
    a = np.cos(th)
    b = np.sin(th)
    vect = abs(a*X + b*Y) < w/2
    near = b*X - a*Y > 0
    far = b*X - a*Y < l
    ends = np.logical_and(far, near)
    phi[np.logical_and(vect, ends)] = 0
"""

# Face
"""
phi[(2*X-0.65)**2 + (Y+0.35)**2 < 0.05] = 0
phi[(2*X+0.65)**2 + (Y+0.35)**2 < 0.05] = 0
phi[(X/2.5)**2 + (2*Y-0.7)**2 < 0.07] = 0
phi[(X/2.5)**2 + (2*Y-0.5)**2 < 0.07] = 1
"""

# Setup grain boundry (casting tube)
mask = X**2 + Y**2 > 1

phi  = np.ma.MaskedArray(phi, mask)
t    = skfmm.distance(phi, dx=1e-3)
print(np.amax(t))
plt.contour(X, Y, phi, [0], linewidths=(2), colors='black')
plt.contour(X, Y, phi.mask, [0], linewidths=(2), colors='red')
plt.contourf(X, Y, t, 20)
plt.show()

plt.imshow(t, interpolation='nearest', cmap=plt.cm.gray)
plt.show()
f

def length(contour):
    offset = np.roll(contour.T, 1, axis = 1)
    l = np.linalg.norm(contour.T - offset, axis = 0)
    return sum(list(l)[1:])

def clean(contour, m = 498):
    offset = np.array([[500, 500]])
    l = np.linalg.norm(contour - offset, axis = 1)
    return contour[l < m]

step = 500

ncontours = int((np.amax(t) * step) + 5)
valid = np.logical_not(mask)
p = [0]
a = [np.count_nonzero(t == 0)]
fig, ax = plt.subplots()
for i in range(0, ncontours, 1):
    contours = measure.find_contours(t, i/step, fully_connected='high')
    p.append(0)
    a.append(np.count_nonzero(np.logical_and(t <= (i/step), valid)))
    for n, contour in enumerate(contours):
        contour = clean(contour)
        p[-1] += length(contour)
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

ax.imshow(t, interpolation='nearest', cmap=plt.cm.gray)
plt.show()
plt.plot(p)
plt.show()
plt.plot(a)
plt.show()
