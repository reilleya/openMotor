from . import geometry
from . import units
from .properties import *

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

class grain(propertyCollection):
    def __init__(self):
        geomName = None
        super().__init__()
        self.props['diameter'] = floatProperty('Diameter', 'm', 0, 1)
        self.props['length'] = floatProperty('Length', 'm', 0, 2)
        self.props['prop'] = propellantProperty('Propellant')

    def setProperties(self, props):
        for p in props.keys():
            self.props[p].setValue(props[p])

    def getProperties(self, props = None):
        if props is None:
            props = self.props.keys()
        return {k:self.props[k].getValue() for k in props}

    def getVolumeSlice(self, r, dR):
        return self.getVolumeAtRegression(r) - self.getVolumeAtRegression(r + dR)

    def getSurfaceAreaAtRegression(self, r):
        return None
    
    def getVolumeAtRegression(self, r):
        return None

    def getWebLeft(self, r):
        return None

    def isWebLeft(self, r):
        return self.getWebLeft(0) < 10000 * self.getWebLeft(r) # Todo: make configurable

    def getMassFlux(self, massIn, dt, r, dr, position):
        return None

    def getPeakMassFlux(self, massIn, dt, r, dr):
        return self.getMassFlux(massIn, dt, r, dr, self.getEndPositions(r)[1]) # Assumes that peak mass flux for each grain is at the port of the grain

    def getEndPositions(self, r): # Returns the positions of the grain ends relative to the original (unburned) grain top
        return None

    def getPortArea(self, r):
        return None

    def getRegressedLength(self, r):
        endPos = self.getEndPositions(r)
        return endPos[1] - endPos[0]

    def getDetailsString(self):
        return 'Length: ' + self.props['length'].dispFormat('in')

    def getMassAtRegression(self, r):
        return self.getVolumeAtRegression(r) * self.props['prop'].getValue()['density']


class batesGrain(grain):
    geomName = "BATES"
    def __init__(self):
        super().__init__()
        self.props['coreDiameter'] = floatProperty('Core Diameter', 'm', 0, 1)
        self.props['inhibitedEnds'] = intProperty('Inhibited ends', '', 0, 3)

    def getSurfaceAreaAtRegression(self, r):
        bLength = self.getRegressedLength(r)
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        diameter = self.props['diameter'].getValue()

        faceArea = geometry.circleArea(diameter) - geometry.circleArea(bCoreDiameter)
        tubeArea = geometry.tubeArea(bCoreDiameter, bLength)

        return tubeArea + (2 * faceArea)

    def getVolumeAtRegression(self, r):
        bLength = self.getRegressedLength(r)
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        diameter = self.props['diameter'].getValue()

        grainVol = geometry.cylinderVolume(diameter, bLength)
        coreVol = geometry.cylinderVolume(bCoreDiameter, bLength)

        return grainVol - coreVol

    def getWebLeft(self, r):
        return self.props['diameter'].getValue() - self.props['coreDiameter'].getValue() - (2 * r)

    def getMassFlux(self, massIn, dt, r, dr, position):
        density = self.props['prop'].getValue()['density']
        diameter = self.props['diameter'].getValue()
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        bLength = self.getRegressedLength(r)
        endPos = self.getEndPositions(r)

        if position < endPos[0]: # If a position above the top face is queried, the mass flow is just the input mass and the diameter is the casting tube
            return massIn / geometry.circleArea(diameter)
        elif position <= endPos[1]: # If a position in the grain is queried, the mass flow is the input mass, from the top face, and from the tube up to the point. The diameter is the core.
            
            if self.props['inhibitedEnds'].getValue() == 1: # Top inhibited
                top = 0
                countedCoreLength = position
            else:
                top = (geometry.circleArea(diameter) - geometry.circleArea(bCoreDiameter + dr)) * dr * density
                countedCoreLength = position - (endPos[0] + dr)
            core = (geometry.cylinderVolume(bCoreDiameter + (2 * dr), countedCoreLength) - geometry.cylinderVolume(bCoreDiameter, countedCoreLength)) * density
            mf = massIn + ((top + core) / dt)
            return mf / geometry.circleArea(bCoreDiameter + (2 * dr))
        else: # A poition past the grain end was specified, so the mass flow includes the input mass flow and all mass produced by the grain. Diameter is the casting tube.
            mf = massIn + (self.getVolumeSlice(r, dr) * density / dt)
            return mf / geometry.circleArea(diameter)

    def getEndPositions(self, r):
        # Until there is some kind of enum prop, inhibited faces are handled like this:
        if self.props['inhibitedEnds'].getValue() == 0: # Neither
            return [r, self.props['length'].getValue() - r]
        elif self.props['inhibitedEnds'].getValue() == 1: # Top
            return [0, self.props['length'].getValue() - r]
        elif self.props['inhibitedEnds'].getValue() == 2: # Bottom
            return [r, self.props['length'].getValue()]
        elif self.props['inhibitedEnds'].getValue() == 3:
            return [0, self.props['length'].getValue()]

    def getPortArea(self, r):
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        return geometry.circleArea(bCoreDiameter)

    def getDetailsString(self):
        return 'Length: ' + self.props['length'].dispFormat('in') + ', Core: ' + self.props['coreDiameter'].dispFormat('in')

class endBurningGrain(grain):
    geomName = 'End Burner'
    def __init__(self):
        super().__init__()

    def getSurfaceAreaAtRegression(self, r):
        diameter = self.props['diameter'].getValue()
        return geometry.circleArea(diameter)

    def getVolumeAtRegression(self, r):
        bLength = self.getRegressedLength(r)
        diameter = self.props['diameter'].getValue()
        return geometry.cylinderVolume(diameter, bLength)

    def getWebLeft(self, r):
        return self.getRegressedLength(r)

    def getMassFlux(self, massIn, dt, r, dr, position):
        return 0 # Should return a simulation error if massIn != 0 
        
    def getEndPositions(self, r):
        return [0, self.props['length'].getValue() - r]

# Generate grain geometry name -> constructor lookup table
grainTypes = {}
grainClasses = [batesGrain, endBurningGrain]
for grainType in grainClasses:
    grainTypes[grainType.geomName] = grainType
