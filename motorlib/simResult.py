"""This module contains the classes that are returned from a simulation, including the main results class and
the channels and components that it is comprised of."""

import math
from . import geometry
from . import units
from .enums.multiValueChannels import MultiValueChannels
from .enums.singleValueChannels import SingleValueChannels


class SimAlert():
    """A sim alert signifies a possible problem with a motor. It has levels of severity including 'error' (simulation
    should not continue or has failed), 'warning' (values entered appear incorrect but can be simulated), and 'message'
    (other information). The type describes the variety of issue the alert is associated with, and the description is
    a human-readable version string with more details about the problem. The location can either be None or a string to
    help the user find the problem."""

    def __init__(self, level, alertType, description, location=None):
        self.level = level
        self.type = alertType
        self.description = description
        self.location = location


class LogChannel():
    """A log channel accepts data from a single source throughout a simulation. It has a human-readable name such as
    'Pressure' to help the user interpret the result, a value type that data passed in will be cast to, and a unit to
    aid in conversion and display. The data type can either be a scalar (float or int) or a list (list or tuple)."""

    def __init__(self, name, valueType, unit):
        if valueType not in (int, float, list, tuple):
            raise TypeError('Value type not in allowed set')
        self.name = name
        self.unit = unit
        self.valueType = valueType
        self.data = []

    def getData(self, unit=None):
        """Return all of the data in the channel, converting it if a type is specified."""
        if unit is None:  # No conversion needed
            return self.data

        if self.valueType in (list, tuple):
            return [[units.convert(d, self.unit, unit) for d in p] for p in self.data]
        # If the data type isn't a list, it should be a scalar
        return [units.convert(p, self.unit, unit) for p in self.data]

    def getPoint(self, i):
        """Returns a specific datapoint by index."""
        return self.data[i]

    def getLast(self):
        """Returns the last datapoint."""
        return self.data[-1]

    def addData(self, data):
        """Adds a new datapoint to the end."""
        self.data.append(data)

    def getAverage(self):
        """Returns the average of the datapoints."""
        if self.valueType in (list, tuple):
            raise NotImplementedError('Average not supported for list types')
        return sum(self.data) / len(self.data)

    def getMax(self):
        """Returns the maximum value of all datapoints. For list datatypes, this operation finds the largest single
        value in any list."""
        if self.valueType in (list, tuple):
            return max([max(l) for l in self.data])
        return max(self.data)

    def getMin(self):
        """Returns the minimum value of all datapoints. For list datatypes, this operation finds the smallest single
        value in any list."""
        if self.valueType in (list, tuple):
            return min([min(l) for l in self.data])
        return min(self.data)


class SimulationResult():
    """A SimulationResult instance contains all results from a single simulation. It has a number of LogChannels, each
    capturing a single stream of outputs from the simulation. It also includes a flag of whether the simulation was
    considered a sucess, along with a list of alerts that the simulation produced while it was running."""

    def __init__(self, motor):
        self.motor = motor

        self.alerts = []
        self.success = False

        self.channels = {
            SingleValueChannels.TIME: LogChannel('Time', float, 's'),
            SingleValueChannels.KN: LogChannel('Kn', float, ''),
            SingleValueChannels.PRESSURE: LogChannel('Chamber Pressure', float, 'Pa'),
            SingleValueChannels.FORCE: LogChannel('Thrust', float, 'N'),
            MultiValueChannels.MASS: LogChannel('Propellant Mass', tuple, 'kg'),
            SingleValueChannels.VOLUME_LOADING: LogChannel('Volume Loading', float, '%'),
            MultiValueChannels.MASS_FLOW: LogChannel('Mass Flow', tuple, 'kg/s'),
            MultiValueChannels.MASS_FLUX: LogChannel('Mass Flux', tuple, 'kg/(m^2*s)'),
            MultiValueChannels.REGRESSION: LogChannel('Regression Depth', tuple, 'm'),
            MultiValueChannels.WEB: LogChannel('Web', tuple, 'm'),
            SingleValueChannels.EXIT_PRESSURE: LogChannel('Nozzle Exit Pressure', float, 'Pa'),
            SingleValueChannels.D_THROAT: LogChannel('Change in Throat Diameter', float, 'm')
        }

    def addAlert(self, alert):
        """Add an entry to the list of alerts for the simulation."""
        self.alerts.append(alert)

    def getBurnTime(self):
        """Returns the burntime of the simulated motor, which is the time from the start when it was last producing
        thrust above the user's defined threshold."""
        return self.channels[SingleValueChannels.TIME].getLast()

    def getInitialKN(self):
        """Returns the motor's Kn before it started firing."""
        return self.channels[SingleValueChannels.KN].getPoint(0)

    def getPeakKN(self):
        """Returns the highest Kn that was observed during the motor's burn."""
        return self.channels[SingleValueChannels.KN].getMax()

    def getAveragePressure(self):
        """Returns the average chamber pressure observed during the simulation."""
        return self.channels[SingleValueChannels.PRESSURE].getAverage()

    def getMaxPressure(self):
        """Returns the highest chamber pressure that was observed during the motor's burn."""
        return self.channels[SingleValueChannels.PRESSURE].getMax()

    def getMinExitPressure(self):
        """Returns the lowest exit pressure that was observed during the motor's burn, ignoring startup and shutdown transients"""
        exit_pressures = self.channels[SingleValueChannels.EXIT_PRESSURE].getData()
        return min(exit_pressures)

    def getPercentBelowThreshold(self, channel, threshold):
        """Returns the total number of seconds spent below a given threshold value"""
        count = 0
        data = self.channels[channel].getData()
        for point in data:
            if point < threshold:
                count += 1
        return count / len(data)

    def getImpulse(self, stop=None):
        """Returns the impulse the simulated motor produced. If 'stop' is set to a value other than None, only the
        impulse to that point in the data is returned."""
        impulse = 0
        lastTime = 0
        for time, force in zip(self.channels[SingleValueChannels.TIME].data[:stop], self.channels[SingleValueChannels.FORCE].data[:stop]):
            impulse += force * (time - lastTime)
            lastTime = time
        return impulse

    def getAverageForce(self):
        """Returns the average force the motor produced during its burn."""
        return self.channels[SingleValueChannels.FORCE].getAverage()

    def getDesignation(self):
        """Returns the standard amateur rocketry designation (H128, M1297) for the motor."""
        imp = self.getImpulse()
        if imp < 1.25:  # This is to avoid a domain error finding log(0)
            return 'N/A'
        return chr(int(math.log(imp / 1.25, 2)) + 65) + str(int(self.getAverageForce()))

    def getFullDesignation(self):
        """Returns the full motor designation, which also includes the total impulse prepended on"""
        return '{:.0f}{}'.format(self.getImpulse(), self.getDesignation())

    def getPeakMassFlux(self):
        """Returns the maximum mass flux observed at any grain end."""
        return self.channels[MultiValueChannels.MASS_FLUX].getMax()

    def getPeakMassFluxLocation(self):
        """Returns the grain number at which the peak mass flux was observed."""
        value = self.getPeakMassFlux()
        # Find the value to get the location
        for frame in self.channels[MultiValueChannels.MASS_FLUX].getData():
            if value in frame:
                return frame.index(value)
        return None

    def getISP(self, index=None):
        """Returns the specific impulse that the simulated motor delivered."""
        if index is None:
            propMass = self.getPropellantMass()
        else:
            propMass = self.getPropellantMass() - self.getPropellantMass(index)
        if propMass == 0:
            return 0
        return self.getImpulse(index) / (propMass * 9.80665)

    def getPortRatio(self):
        """Returns the port/throat ratio of the motor, or None if it doesn't have a port."""
        aftPort = self.motor.grains[-1].getPortArea(0)
        if aftPort is not None:
            return aftPort / geometry.circleArea(self.motor.nozzle.props['throat'].getValue())
        return None

    def getPropellantLength(self):
        """Returns the total length of all propellant before the simulated burn."""
        return sum([g.props['length'].getValue() for g in self.motor.grains])

    def getPropellantMass(self, index=0):
        """Returns the total mass of all propellant before the simulated burn. Optionally accepts a index that the mass
        will be sampled at."""
        return sum(self.channels[MultiValueChannels.MASS].getPoint(index))

    def getVolumeLoading(self, index=0):
        """Returns the percentage of the motor's volume occupied by propellant. Optionally accepts a index that the
        value will be sampled at."""
        return self.channels[SingleValueChannels.VOLUME_LOADING].getPoint(index)

    def getIdealThrustCoefficient(self):
        """Returns the motor's thrust coefficient for the average pressure during the burn and no throat diameter
        changes or performance losses."""
        chamberPres = self.getAveragePressure()
        _, _, gamma, _, _ = self.motor.propellant.getCombustionProperties(chamberPres)
        ambPressure = self.motor.config.getProperty('ambPressure')
        return self.motor.nozzle.getIdealThrustCoeff(chamberPres, ambPressure, gamma, 0)

    def getAdjustedThrustCoefficient(self):
        """Returns the motor's thrust coefficient for the average pressure during the burn and no throat diameter
        changes, but including performance losses."""
        chamberPres = self.getAveragePressure()
        _, _, gamma, _, _ = self.motor.propellant.getCombustionProperties(chamberPres)
        ambPressure = self.motor.config.getProperty('ambPressure')
        return self.motor.nozzle.getAdjustedThrustCoeff(chamberPres, ambPressure, gamma, 0)

    def getAlertsByLevel(self, level):
        """Returns all simulation alerts of the specified level."""
        out = []
        for alert in self.alerts:
            if alert.level == level:
                out.append(alert)
        return out

    def shouldContinueSim(self, thrustThres):
        """Returns if the simulation should continue based on the thrust from the last timestep."""
        # With only one data point, there is nothing to compare
        if len(self.channels[SingleValueChannels.TIME].getData()) == 1:
            return True
        # Otherwise perform the comparison. 0.01 converts the threshold to a %
        return self.channels[SingleValueChannels.FORCE].getLast() > thrustThres * 0.01 * self.channels[SingleValueChannels.FORCE].getMax()

    def getCSV(self, pref=None, exclude=[], excludeGrains=[]):
        """Returns a string that contains a CSV of the simulated data. Preferences can be passed in to set units that
        the values will be converted to. All log channels are included unless their names are in the include
        argument. """
        out = ''
        outUnits = {}
        for chan in self.channels:
            if chan in exclude:
                continue
            # Get unit from preferences
            if pref is not None:
                outUnits[chan] = pref.getUnit(self.channels[chan].unit)
            else:
                outUnits[chan] = self.channels[chan].unit
            # Add title for column
            if self.channels[chan].valueType in (float, int):
                out += self.channels[chan].name
                if outUnits[chan] != '':
                    out += '({})'.format(outUnits[chan])
                out += ','
            elif self.channels[chan].valueType in (list, tuple):
                for grain in range(1, len(self.channels[chan].getLast()) + 1):
                    if grain - 1 not in excludeGrains:
                        out += self.channels[chan].name + '('
                        out += 'G{}'.format(grain)
                        if outUnits[chan] != '':
                            out += ';{}'.format(outUnits[chan])
                        out += '),'

        out = out[:-1]  # Remove the last comma
        out += '\n'

        places = 5
        for ind, time in enumerate(self.channels[SingleValueChannels.TIME].getData()):
            out += str(round(time, places)) + ','
            for chan in self.channels:
                if chan in exclude:
                    continue
                if chan != SingleValueChannels.TIME:
                    if self.channels[chan].valueType in (float, int):
                        orig = self.channels[chan].getPoint(ind)
                        conv = units.convert(orig, self.channels[chan].unit, outUnits[chan])
                        rounded = round(conv, places)
                        out += str(rounded) + ','
                    elif self.channels[chan].valueType in (list, tuple):
                        for gid, grainVal in enumerate(self.channels[chan].getPoint(ind)):
                            if gid not in excludeGrains:
                                conv = round(units.convert(grainVal, self.channels[chan].unit, outUnits[chan]), places)
                                out += str(conv) + ','

            out = out[:-1]  # Remove the last comma
            out += '\n'

        return out
