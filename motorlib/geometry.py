"""This module includes the geometry methods that openMotor uses in its calculations"""

import math
import numpy as np

def circleArea(dia):
    """Returns the area of a circle with diameter dia"""
    return ((dia / 2) ** 2) * math.pi

def circlePerimeter(dia):
    """Returns the perimeter (circumference) of a circle with diameter dia"""
    return dia * math.pi

def circleDiameterFromArea(area):
    """Returns the diameter of a circle with area 'area'"""
    return 2 * ((area / math.pi) ** 0.5)

def tubeArea(dia, height):
    """Returns the surface area of a tube (cylinder without endcaps) with diameter 'dia' and height 'height'"""
    return dia * math.pi * height

def cylinderArea(dia, height):
    """Returns the surface area of a cylinder with diameter 'dia' and height 'height'"""
    return (2 * circleArea(dia)) + (tubeArea(dia, height))

def cylinderVolume(dia, height):
    """Returns the volume of a cylinder with diameter 'dia' and height 'height'"""
    return height * circleArea(dia)

def frustrumLateralSurfaceArea(diameterA, diameterB, length):
    radiusA = diameterA / 2
    radiusB = diameterB / 2
    return math.pi * (radiusA + radiusB) * (abs(radiusA - radiusB) ** 2 + length ** 2) ** 0.5

def frustrumVolume(diameterA, diameterB, length):
    radiusA = diameterA / 2
    radiusB = diameterB / 2
    return math.pi * (length / 3) * (radiusA ** 2 + radiusA * radiusB + radiusB ** 2)

def length(contour, mapSize, tolerance=3):
    """Returns the total length of all segments in a contour that aren't within 'tolerance' of the edge of a
    circle with diameter 'mapSize'"""
    offset = np.roll(contour.T, 1, axis=1)
    lengths = np.linalg.norm(contour.T - offset, axis=0)

    centerOffset = np.array([[mapSize / 2, mapSize / 2]])
    radius = np.linalg.norm(contour - centerOffset, axis=1)

    valid = radius < (mapSize / 2) - tolerance

    return np.sum(lengths[valid])

def clean(contour, mapSize, tolerance):
    """Returns a contour with the same points as the input, omitting any within 'tolerace' of a circle of
    diameter 'mapSize'"""
    offset = np.array([[mapSize / 2, mapSize / 2]])
    lengths = np.linalg.norm(contour - offset, axis=1)
    return contour[lengths < (mapSize / 2) - tolerance]

def dist(point1, point2):
    """Returns the distance between two points [x1, y1], [x2, y2]"""
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
