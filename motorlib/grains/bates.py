from .. import grain
from .. import geometry
from .. import simAlert, simAlertLevel, simAlertType
from ..properties import *

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

    def getGeometryErrors(self):
        errors = super().getGeometryErrors()
        if self.props['coreDiameter'].getValue() == 0:
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Core diameter must not be 0'))
        if self.props['coreDiameter'].getValue() >= self.props['diameter'].getValue():
            errors.append(simAlert(simAlertLevel.ERROR, simAlertType.GEOMETRY, 'Core diameter must be less than grain diameter'))
        return errors
