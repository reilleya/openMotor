from .. import grain
from ..import geometry
from ..properties import *

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
