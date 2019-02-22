from . import geometry
from . import units
from .properties import *

class grain(propertyCollection):
    def __init__(self):
        geomName = None
        super().__init__()
        self.props['diameter'] = floatProperty('Diameter', 'm', 0, 1)
        self.props['length'] = floatProperty('Length', 'm', 0, 2)

    def getVolumeSlice(self, r, dR):
        return self.getVolumeAtRegression(r) - self.getVolumeAtRegression(r + dR)

    def getSurfaceAreaAtRegression(self, r):
        return None
    
    def getVolumeAtRegression(self, r):
        return None

    def getWebLeft(self, r): # Returns the shortest distance the grain has to regress to burn out
        return None

    def isWebLeft(self, r, burnoutThres = 0.00001):
        return self.getWebLeft(r) > burnoutThres

    def getMassFlux(self, massIn, dt, r, dr, position, density):
        return None

    def getPeakMassFlux(self, massIn, dt, r, dr, density):
        return self.getMassFlux(massIn, dt, r, dr, self.getEndPositions(r)[1], density) # Assumes that peak mass flux for each grain is at the port of the grain

    def getEndPositions(self, r): # Returns the positions of the grain ends relative to the original (unburned) grain top
        return None

    def getPortArea(self, r):
        return None

    def getRegressedLength(self, r):
        endPos = self.getEndPositions(r)
        return endPos[1] - endPos[0]

    def getDetailsString(self, preferences):
        return 'Length: ' + self.props['length'].dispFormat(preferences.units.getProperty('m'))


class batesGrain(grain):
    geomName = "BATES"
    def __init__(self):
        super().__init__()
        self.props['coreDiameter'] = floatProperty('Core Diameter', 'm', 0, 1)
        self.props['inhibitedEnds'] = enumProperty('Inhibited ends', ['Neither', 'Top', 'Bottom', 'Both'])

    def getSurfaceAreaAtRegression(self, r):
        bLength = self.getRegressedLength(r)
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        diameter = self.props['diameter'].getValue()

        faceArea = geometry.circleArea(diameter) - geometry.circleArea(bCoreDiameter)
        exposedFaces = 2
        if self.props['inhibitedEnds'].getValue() == 'Top' or self.props['inhibitedEnds'].getValue() == 'Bottom':
            exposedFaces = 1
        if self.props['inhibitedEnds'].getValue() == 'Both':
            exposedFaces = 0

        tubeArea = geometry.tubeArea(bCoreDiameter, bLength)

        return tubeArea + (exposedFaces * faceArea)

    def getVolumeAtRegression(self, r):
        bLength = self.getRegressedLength(r)
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        diameter = self.props['diameter'].getValue()

        grainVol = geometry.cylinderVolume(diameter, bLength)
        coreVol = geometry.cylinderVolume(bCoreDiameter, bLength)

        return grainVol - coreVol

    def getWebLeft(self, r):
        web = self.props['diameter'].getValue() - self.props['coreDiameter'].getValue() - (2 * r)
        length = self.getRegressedLength(r)
        return min(web, length)

    def getMassFlux(self, massIn, dt, r, dr, position, density):
        diameter = self.props['diameter'].getValue()
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        bLength = self.getRegressedLength(r)
        endPos = self.getEndPositions(r)

        if position < endPos[0]: # If a position above the top face is queried, the mass flow is just the input mass and the diameter is the casting tube
            return massIn / geometry.circleArea(diameter)
        elif position <= endPos[1]: # If a position in the grain is queried, the mass flow is the input mass, from the top face, and from the tube up to the point. The diameter is the core.
            
            if self.props['inhibitedEnds'].getValue() == 'Top': # Top inhibited
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
        if self.props['inhibitedEnds'].getValue() == 'Neither': # Neither
            return [r, self.props['length'].getValue() - r]
        elif self.props['inhibitedEnds'].getValue() == 'Top': # Top
            return [0, self.props['length'].getValue() - r]
        elif self.props['inhibitedEnds'].getValue() == 'Bottom': # Bottom
            return [r, self.props['length'].getValue()]
        elif self.props['inhibitedEnds'].getValue() == 'Both':
            return [0, self.props['length'].getValue()]

    def getPortArea(self, r):
        bCoreDiameter = self.props['coreDiameter'].getValue() + (r * 2)
        return geometry.circleArea(bCoreDiameter)

    def getDetailsString(self, preferences):
        lengthUnit = preferences.units.getProperty('m')
        return 'Length: ' + self.props['length'].dispFormat(lengthUnit) + ', Core: ' + self.props['coreDiameter'].dispFormat(lengthUnit)

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

    def getMassFlux(self, massIn, dt, r, dr, position, density):
        return 0 # Should return a simulation error if massIn != 0 
        
    def getEndPositions(self, r):
        return [0, self.props['length'].getValue() - r]

# Generate grain geometry name -> constructor lookup table
grainTypes = {}
grainClasses = [batesGrain, endBurningGrain]
for grainType in grainClasses:
    grainTypes[grainType.geomName] = grainType
