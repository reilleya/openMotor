from . import geometry
from . import units

import math
from enum import Enum

class simAlertLevel(Enum):
    ERROR = 1
    WARNING = 2
    MESSAGE = 3

class simAlertType(Enum):
    GEOMETRY = 1
    CONSTRAINT = 2

alertLevelNames = {
                    simAlertLevel.ERROR: 'Error',
                    simAlertLevel.WARNING: 'Warning',
                    simAlertLevel.MESSAGE: 'Message'
                }

alertTypeNames = {
                    simAlertType.GEOMETRY: 'Geometry',
                    simAlertType.CONSTRAINT: 'Constraint'
                }

class simAlert():
    def __init__(self, level, alertType, description, location = None):
        self.level = level
        self.type = alertType
        self.description = description
        self.location = location


class logChannel():
    def __init__(self, name, valueType, unit):
        if valueType not in (int, float, list, tuple):
            raise TypeError('Value type not in allowed set')
        self.name = name
        self.unit = unit
        self.valueType = valueType
        self.data = []

    def getData(self, unit = None):
        if unit is None:
            return self.data
        else:
            if self.valueType in (int, float):
                return [units.convert(p, self.unit, unit) for p in self.data]
            elif self.valueType in (list, tuple):
                return [[units.convert(d, self.unit, unit) for d in p] for p in self.data]

    def getPoint(self, i):
        return self.data[i]

    def getLast(self):
        return self.data[-1]

    def addData(self, data):
        self.data.append(data)

    def getAverage(self):
        if self.valueType in (int, float):
            return sum(self.data) / len(self.data)
        elif self.valueType in (list, tuple):
            raise NotImplementedError('Average not supported for list types')

    def getMax(self):
        if self.valueType in (int, float):
            return max(self.data)
        elif self.valueType in (list, tuple):
            return max([max(l) for l in self.data])


class simulationResult():
    def __init__(self, motor):
        self.motor = motor

        self.alerts = []
        self.success = False

        self.channels = {
                            'time': logChannel('Time', float, 's'),
                            'kn': logChannel('Kn', float, ''),
                            'pressure': logChannel('Chamber Pressure', float, 'Pa'),
                            'force': logChannel('Thrust', float, 'N'),
                            'mass': logChannel('Propellant Mass', tuple, 'kg'),
                            'massFlow': logChannel('Mass Flow', tuple, 'kg/s'),
                            'massFlux': logChannel('Mass Flux', tuple, 'kg/(m^2*s)')
                        }

    def addAlert(self, alert):
        self.alerts.append(alert)

    def getBurnTime(self):
        return self.channels['time'].getLast()

    def getInitialKN(self):
        return self.channels['kn'].getPoint(1)

    def getPeakKN(self):
        return self.channels['kn'].getMax()

    def getAveragePressure(self):
        return self.channels['pressure'].getAverage()

    def getMaxPressure(self):
        return self.channels['pressure'].getMax()

    def getImpulse(self):
        impulse = 0
        lastTime = 0
        for time, force in zip(self.channels['time'].data, self.channels['force'].data):
            impulse += force * (time - lastTime)
            lastTime = time
        return impulse

    def getAverageForce(self):
        return self.channels['force'].getAverage()

    def getDesignation(self):
        imp = self.getImpulse()
        if imp == 0: # This is to avoid a domain error finding log(0)
            return 'N/A'
        return chr(int(math.log(imp/2.5, 2)) + 66) + str(int(self.getAverageForce()))

    def getPeakMassFlux(self):
        return self.channels['massFlux'].getMax()

    def getPeakMassFluxLocation(self):
        value = self.getPeakMassFlux()
        # Find the value to get the location
        for frame in self.channels['massFlux'].getData():
            if value in frame:
                return frame.index(value)

    def getISP(self):
        return self.getImpulse() / (self.getPropellantMass() * 9.80665)

    def getPortRatio(self):
        aftPort = self.motor.grains[-1].getPortArea(0)
        if aftPort is not None:
            return aftPort / geometry.circleArea(self.motor.nozzle.props['throat'].getValue())
        else:
            return None

    def getPropellantLength(self):
        return sum([g.props['length'].getValue() for g in self.motor.grains])

    def getPropellantMass(self):
        return sum(self.channels['mass'].getPoint(0))

    def getAlertsByLevel(self, level):
        out = []
        for alert in self.alerts:
            if alert.level == level:
                out.append(alert)
        return out

    def getCSV(self, pref = None, exclude = []):
        out = ''
        outUnits = {}
        for ch in self.channels:
            if ch in exclude:
                continue
            # Get unit from preferences
            if pref is not None:
                outUnits[ch] = pref.getUnit(self.channels[ch].unit)
            else:
                outUnits[ch] = self.channels[ch].unit
            # Add title for column
            if self.channels[ch].valueType in (float, int):
                out += self.channels[ch].name
                if outUnits[ch] != '':
                    out += '(' + outUnits[ch] + ')'
                out += ','
            elif self.channels[ch].valueType in (list, tuple):
                for grain in range(1, len(self.channels[ch].getLast()) + 1):
                    out += self.channels[ch].name + '('
                    out += 'G' + str(grain)
                    if outUnits[ch] != '':
                        out += ';' + outUnits[ch]
                    out += '),'

        out = out[:-1] # Remove the last comma
        out += '\n'

        places = 5
        for ind, t in enumerate(self.channels['time'].getData()):
            out += str(round(t, places)) + ','
            for ch in self.channels:
                if ch in exclude:
                    continue
                if ch != 'time':
                    if self.channels[ch].valueType in (float, int):
                        conv = round(units.convert(self.channels[ch].getPoint(ind), self.channels[ch].unit, outUnits[ch]), places)
                        out += str(conv) + ','
                    elif self.channels[ch].valueType in (list, tuple):
                        for grainVal in self.channels[ch].getPoint(ind):
                            conv = round(units.convert(grainVal, self.channels[ch].unit, outUnits[ch]), places)
                            out += str(conv) + ','

            out = out[:-1] # Remove the last comma
            out += '\n'

        return out
