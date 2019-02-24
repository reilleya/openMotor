import matplotlib
matplotlib.use('Qt4Agg')


import numpy as np
import pylab as plt
import skfmm


X, Y = np.meshgrid(np.linspace(-1,1,1001), np.linspace(-1,1,1001))
phi = np.ones_like(X)
phi[np.logical_and(np.abs(Y)<0.15, np.abs(X)<0.7)] = 0
phi[np.logical_and(np.abs(X)<0.15, np.abs(Y)<0.7)] = 0

phi[np.logical_and(X+Y<0.2, X+Y>-0.2, np.logical_not(Y-X < 0.3))] = 0
#phi[np.logical_and(-X+Y<0.25, -X+Y>0.1)] = 0

phi[X**2 + Y**2 < 0.175] = 0
# Setup grain boundry (casting tube)
mask = X**2 + Y**2 > 1
phi  = np.ma.MaskedArray(phi, mask)
t    = skfmm.distance(phi, dx=1e-3)
plt.contour(X, Y, phi, [0], linewidths=(3), colors='black')
plt.contour(X, Y, phi.mask, [0], linewidths=(3), colors='red')
plt.contourf(X, Y, t, 10)
#plt.colorbar()
plt.show()
#print(t[250, 300])
#plt.contour(X, Y, phi, [0], linewidths=(3), colors='black')
#plt.contour(X, Y, phi.mask, [0], linewidths=(3), colors='red')
#print(plt.contour(X, Y, t, 100))


#plt.scatter(X[np.logical_and(np.abs(t - 0.11) < 0.0005, X**2 + Y**2 < 1)], Y[np.logical_and(np.abs(t - 0.11) < 0.0005, X**2 + Y**2 < 1)])#print(np.count_nonzero(np.abs(t - 0.15) < 0.0001))#plt.colorbar()
#plt.show()

def length(contour):
    #print(contour.T)
    offset = np.roll(contour.T, 1, axis = 1)
    #print(offset)
    #print(contour.T - offset)
    l = np.linalg.norm(contour.T - offset, axis = 0)
    #print(l)
    return sum(l)

def clean(contour, m = 498):
    offset = np.array([[500, 500]])
    l = np.linalg.norm(contour - offset, axis = 1)
    return contour[l < m]


test = np.array([[-1, -1], [1, -1], [1, 2], [-1, 1]])
#print(length(test))

clean(test)



from skimage import measure

p = [0]

fig, ax = plt.subplots()

for i in range(0, 150, 5):

    contours = measure.find_contours(t, i/500, fully_connected='high')

    #fig, ax = plt.subplots()
    #ax.imshow(t, interpolation='nearest', cmap=plt.cm.gray)
    p.append(0)
    for n, contour in enumerate(contours):
        contour = clean(contour)
        p[-1] += length(contour)
            #print(length(contour))
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

    #ax.axis('image')
    #ax.set_xticks([])
    #ax.set_yticks([])
    #plt.show()


ax.imshow(t, interpolation='nearest', cmap=plt.cm.gray)
plt.show()
plt.plot(p)
plt.show()