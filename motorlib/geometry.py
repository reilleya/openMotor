import math
import numpy as np

def circleArea(d):
    return ((d / 2) ** 2) * math.pi

def circlePerimeter(d):
    return d * math.pi

def circleDiameterFromArea(a):
    return 2*((a / math.pi) ** 0.5)

def tubeArea(d, h):
    return d * math.pi * h

def cylinderArea(d, h):
    return (2 * circleArea(d)) + (tubeArea(d, h))

def cylinderVolume(d, h):
    return h * circleArea(d)

def length(contour): # Adds up the length of each segment in a contour
    offset = np.roll(contour.T, 1, axis = 1)
    l = np.linalg.norm(contour.T - offset, axis = 0)
    return sum(list(l)[1:])

def clean(contour, mapSize, tolerance): # Removes the points in a contour near the edge (inhibits the casting tube)
    offset = np.array([[mapSize / 2, mapSize / 2]])
    l = np.linalg.norm(contour - offset, axis = 1)
    return contour[l < (mapSize / 2) - tolerance]
