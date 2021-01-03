"""End Burner submodule"""

from ..grain import Grain
from ..import geometry

class EndBurningGrain(Grain):
    """Defines an end-burning grain, which is a simple cylinder that burns on one end."""
    geomName = 'End Burner'

    def getSurfaceAreaAtRegression(self, regDist):
        diameter = self.props['diameter'].getValue()
        return geometry.circleArea(diameter)

    def getVolumeAtRegression(self, regDist):
        bLength = self.getRegressedLength(regDist)
        diameter = self.props['diameter'].getValue()
        return geometry.cylinderVolume(diameter, bLength)

    def simulationSetup(self, config):
        pass

    def getWebLeft(self, regDist):
        return self.getRegressedLength(regDist)

    def getMassFlux(self, massIn, dTime, regDist, dRegDist, position, density):
        return 0

    def getPortArea(self, regDist):
        return None

    def getEndPositions(self, regDist):
        return (0, self.props['length'].getValue() - regDist)
