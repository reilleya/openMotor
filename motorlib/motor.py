"""Conains the motor class and a supporting configuration property collection."""
from .grains import grainTypes
from .nozzle import Nozzle
from .propellant import Propellant
from . import geometry
from .simResult import SimulationResult, SimAlert, SimAlertLevel, SimAlertType
from .grains import EndBurningGrain
from .properties import PropertyCollection, FloatProperty, IntProperty
from .constants import gasConstant

class MotorConfig(PropertyCollection):
    """Contains the settings required for simulation, including environmental conditions and details about
    how to run the simulation."""
    def __init__(self):
        super().__init__()
        # Limits
        self.props['maxPressure'] = FloatProperty('Maximum Allowed Pressure', 'Pa', 0, 7e7)
        self.props['maxMassFlux'] = FloatProperty('Maximum Allowed Mass Flux', 'kg/(m^2*s)', 0, 1e4)
        self.props['minPortThroat'] = FloatProperty('Minimum Allowed Port/Throat Ratio', '', 1, 4)
        # Simulation
        self.props['burnoutWebThres'] = FloatProperty('Web Burnout Threshold', 'm', 2.54e-5, 3.175e-3)
        self.props['burnoutThrustThres'] = FloatProperty('Thrust Burnout Threshold', '%', 0.01, 10)
        self.props['timestep'] = FloatProperty('Simulation Timestep', 's', 0.0001, 0.1)
        self.props['ambPressure'] = FloatProperty('Ambient Pressure', 'Pa', 0.0001, 102000)
        self.props['mapDim'] = IntProperty('Grain Map Dimension', '', 250, 2000)


class Motor():
    """The motor class stores a number of grains, a nozzle instance, a propellant, and a configuration that it uses
    to run simulations. Simulations return a simRes object that includes any warnings or errors associated with the
    simulation and the data. The propellant field may be None if the motor has no propellant set, and the grains list
    is allowed to be empty. The nozzle field and config must be filled, even if they are empty property collections."""
    def __init__(self, propDict=None):
        self.grains = []
        self.propellant = None
        self.nozzle = Nozzle()
        self.config = MotorConfig()

        if propDict is not None:
            self.applyDict(propDict)

    def getDict(self):
        """Returns a serializable representation of the motor. The dictionary has keys 'nozzle', 'propellant',
        'grains', and 'config', which hold to the properties of their corresponding fields. Grains is a list
        of dicts, each containing a type and properties. Propellant may be None if the motor has no propellant
        set."""
        motorData = {}
        motorData['nozzle'] = self.nozzle.getProperties()
        if self.propellant is not None:
            motorData['propellant'] = self.propellant.getProperties()
        else:
            motorData['propellant'] = None
        motorData['grains'] = [{'type': grain.geomName, 'properties': grain.getProperties()} for grain in self.grains]
        motorData['config'] = self.config.getProperties()
        return motorData

    def applyDict(self, dictionary):
        """Makes the motor copy properties from the dictionary that is passed in, which must be formatted like
        the result passed out by 'getDict'"""
        self.nozzle.setProperties(dictionary['nozzle'])
        if dictionary['propellant'] is not None:
            self.propellant = Propellant(dictionary['propellant'])
        else:
            self.propellant = None
        self.grains = []
        for entry in dictionary['grains']:
            self.grains.append(grainTypes[entry['type']]())
            self.grains[-1].setProperties(entry['properties'])
        self.config.setProperties(dictionary['config'])

    def calcKN(self, regDepth, dThroat):
        """Returns the motor's Kn when it has each grain has regressed by its value in regDepth, which should be a list
        with the same number of elements as there are grains in the motor."""
        burnoutThres = self.config.getProperty('burnoutWebThres')
        gWithReg = zip(self.grains, regDepth)
        perGrain = [gr.getSurfaceAreaAtRegression(reg) * int(gr.isWebLeft(reg, burnoutThres)) for gr, reg in gWithReg]
        surfArea = sum(perGrain)
        nozz = self.nozzle.getThroatArea(dThroat)
        return surfArea / nozz

    def calcIdealPressure(self, regDepth, dThroat, kn=None):
        """Returns the steady-state pressure of the motor at a given reg. Kn is calculated automatically, but it can
        optionally be passed in to save time on motors where calculating surface area is expensive."""
        if kn is None:
            kn = self.calcKN(regDepth, dThroat)
        density = self.propellant.getProperty('density')
        tabPressures = []
        for tab in self.propellant.getProperty('tabs'):
            ballA, ballN, gamma, temp, molarMass = tab['a'], tab['n'], tab['k'], tab['t'], tab['m']
            num = kn * density * ballA
            exponent = 1 / (1 - ballN)
            denom = ((gamma / ((gasConstant / molarMass) * temp)) * ((2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1)))) ** 0.5
            tabPressure = (num / denom) ** exponent
            # If the pressure that a burnrate produces falls into its range, we know it is the proper burnrate
            # We have to slightly widen the range allowed for each burnrate to allow for floating point error
            adjMax = 1.001 * tab['maxPressure']
            adjMin = 0.999 * tab['minPressure']
            if tab['minPressure'] == self.propellant.getMinimumValidPressure() and tabPressure < adjMax:
                return tabPressure
            if tab['maxPressure'] == self.propellant.getMaximumValidPressure() and adjMin < tabPressure:
                return tabPressure
            if adjMin < tabPressure < adjMax:
                return tabPressure

    def calcIdealThrustCoeff(self, chamberPres, dThroat, exitPres=None):
        """Calculates C_f, the ideal thrust coefficient for the motor's nozzle and propellant, and the given chamber
        pressure. If nozzle exit presure isn't provided, it will be calculated."""
        if chamberPres == 0:
            return 0

        _, _, gamma, _, _ = self.propellant.getCombustionProperties(chamberPres)
        if exitPres is None:
            exitPres = self.nozzle.getExitPressure(gamma, chamberPres)
        ambPres = self.config.getProperty("ambPressure")
        exitArea = self.nozzle.getExitArea()
        throatArea = self.nozzle.getThroatArea(dThroat)

        term1 = (2 * (gamma**2)) / (gamma - 1)
        term2 = (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))
        term3 = 1 - ((exitPres / chamberPres) ** ((gamma - 1) / gamma))

        momentumThrust = (term1 * term2 * term3) ** 0.5
        pressureThrust = ((exitPres - ambPres) * exitArea) / (throatArea * chamberPres)

        return momentumThrust + pressureThrust

    def calcForce(self, chamberPres, dThroat, exitPres=None):
        """Calculates the force of the motor at a given regression depth per grain. Calculates exit pressure by
        default, but can also use a value passed in. This method uses a combination of the techniques described
        in these resources to adjust the thrust coefficient: https://apps.dtic.mil/dtic/tr/fulltext/u2/a099791.pdf
        and http://rasaero.com/dloads/Departures%20from%20Ideal%20Performance.pdf."""
        thrustCoeffIdeal = self.calcIdealThrustCoeff(chamberPres, dThroat, exitPres)
        divLoss = self.nozzle.getDivergenceLosses()
        throatLoss = self.nozzle.getThroatLosses(dThroat)
        skinLoss = self.nozzle.getSkinLosses()
        efficiency = self.nozzle.getProperty('efficiency')
        thrustCoeffAdj = divLoss * throatLoss * efficiency * (skinLoss * thrustCoeffIdeal + (1 - skinLoss))
        thrust = thrustCoeffAdj * self.nozzle.getThroatArea(dThroat) * chamberPres
        return max(thrust, 0)

    def calcFreeVolume(self, regDepth):
        """Calculates the volume inside of the motor not occupied by proppellant for a set of regression depths."""
        return sum([grain.getFreeVolume(reg) for grain, reg in zip(self.grains, regDepth)])

    def calcTotalVolume(self):
        """Calculates the bounding-cylinder volume of the combustion chamber."""
        return sum([grain.getGrainBoundingVolume() for grain in self.grains])

    def runSimulation(self, callback=None):
        """Runs a simulation of the motor and returns a simRes instance with the results. Constraints are checked,
        including the number of grains, if the motor has a propellant set, and if the grains have geometry errors. If
        all of these tests are passed, the motor's operation is simulated by calculating Kn, using this value to get
        pressure, and using pressure to determine thrust and other statistics. The next timestep is then prepared by
        using the pressure to determine how the motor will regress in the given timestep at the current pressure.
        This process is repeated and regression tracked until all grains have burned out, when the results and any
        warnings are returned."""
        burnoutWebThres = self.config.getProperty('burnoutWebThres')
        burnoutThrustThres = self.config.getProperty('burnoutThrustThres')
        dTime = self.config.getProperty('timestep')

        simRes = SimulationResult(self)

        # Check for geometry errors
        if len(self.grains) == 0:
            aText = 'Motor must have at least one propellant grain'
            simRes.addAlert(SimAlert(SimAlertLevel.ERROR, SimAlertType.CONSTRAINT, aText, 'Motor'))
        for gid, grain in enumerate(self.grains):
            if isinstance(grain, EndBurningGrain) and gid != 0: # Endburners have to be at the foward end
                aText = 'End burning grains must be the forward-most grain in the motor'
                simRes.addAlert(SimAlert(SimAlertLevel.ERROR, SimAlertType.CONSTRAINT, aText, 'Grain ' + str(gid + 1)))
            for alert in grain.getGeometryErrors():
                alert.location = 'Grain ' + str(gid + 1)
                simRes.addAlert(alert)
        for alert in self.nozzle.getGeometryErrors():
            simRes.addAlert(alert)

        # Make sure the motor has a propellant set
        if self.propellant is None:
            alert = SimAlert(SimAlertLevel.ERROR, SimAlertType.CONSTRAINT, 'Motor must have a propellant set', 'Motor')
            simRes.addAlert(alert)
        else:
            for alert in self.propellant.getErrors():
                simRes.addAlert(alert)

        # If any errors occurred, stop simulation and return an empty sim with errors
        if len(simRes.getAlertsByLevel(SimAlertLevel.ERROR)) > 0:
            return simRes

        # Pull the required numbers from the propellant
        density = self.propellant.getProperty('density')

        # Precalculate these are they don't change
        motorVolume = self.calcTotalVolume()

        # Generate coremaps for perforated grains
        for grain in self.grains:
            grain.simulationSetup(self.config)

        # Setup initial values
        perGrainReg = [0 for grain in self.grains]

        # At t = 0, the motor has ignited
        simRes.channels['time'].addData(0)
        simRes.channels['kn'].addData(self.calcKN(perGrainReg, 0))
        simRes.channels['pressure'].addData(self.calcIdealPressure(perGrainReg, 0, None))
        simRes.channels['force'].addData(0)
        simRes.channels['mass'].addData([grain.getVolumeAtRegression(0) * density for grain in self.grains])
        simRes.channels['volumeLoading'].addData(100 * (1 - (self.calcFreeVolume(perGrainReg) / motorVolume)))
        simRes.channels['massFlow'].addData([0 for grain in self.grains])
        simRes.channels['massFlux'].addData([0 for grain in self.grains])
        simRes.channels['regression'].addData([0 for grains in self.grains])
        simRes.channels['web'].addData([grain.getWebLeft(0) for grain in self.grains])
        simRes.channels['exitPressure'].addData(0)
        simRes.channels['dThroat'].addData(0)

        # Check port/throat ratio and add a warning if it is large enough
        aftPort = self.grains[-1].getPortArea(0)
        if aftPort is not None:
            minAllowed = self.config.getProperty('minPortThroat')
            ratio = aftPort / geometry.circleArea(self.nozzle.props['throat'].getValue())
            if ratio < minAllowed:
                desc = 'Initial port/throat ratio of ' + str(round(ratio, 3)) + ' was less than ' + str(minAllowed)
                simRes.addAlert(SimAlert(SimAlertLevel.WARNING, SimAlertType.CONSTRAINT, desc, 'N/A'))

        # Perform timesteps
        while simRes.shouldContinueSim(burnoutThrustThres):
            # Calculate regression
            massFlow = 0
            perGrainMass = [0 for grain in self.grains]
            perGrainMassFlow = [0 for grain in self.grains]
            perGrainMassFlux = [0 for grain in self.grains]
            perGrainWeb = [0 for grain in self.grains]
            for gid, grain in enumerate(self.grains):
                if grain.getWebLeft(perGrainReg[gid]) > burnoutWebThres:
                    # Calculate regression at the current pressure
                    reg = dTime * self.propellant.getBurnRate(simRes.channels['pressure'].getLast())
                    # Find the mass flux through the grain based on the mass flow fed into from grains above it
                    perGrainMassFlux[gid] = grain.getPeakMassFlux(massFlow, dTime, perGrainReg[gid], reg, density)
                    # Find the mass of the grain after regression
                    perGrainMass[gid] = grain.getVolumeAtRegression(perGrainReg[gid]) * density
                    # Add the change in grain mass to the mass flow
                    massFlow += (simRes.channels['mass'].getLast()[gid] - perGrainMass[gid]) / dTime
                    # Apply the regression
                    perGrainReg[gid] += reg
                    perGrainWeb[gid] = grain.getWebLeft(perGrainReg[gid])
                perGrainMassFlow[gid] = massFlow
            simRes.channels['regression'].addData(perGrainReg[:])
            simRes.channels['web'].addData(perGrainWeb)

            simRes.channels['volumeLoading'].addData(100 * (1 - (self.calcFreeVolume(perGrainReg) / motorVolume)))
            simRes.channels['mass'].addData(perGrainMass)
            simRes.channels['massFlow'].addData(perGrainMassFlow)
            simRes.channels['massFlux'].addData(perGrainMassFlux)

            # Calculate KN
            dThroat = simRes.channels['dThroat'].getLast()
            simRes.channels['kn'].addData(self.calcKN(perGrainReg, dThroat))

            # Calculate Pressure
            lastKn = simRes.channels['kn'].getLast()
            pressure = self.calcIdealPressure(perGrainReg, dThroat, lastKn)
            simRes.channels['pressure'].addData(pressure)

            # Calculate Exit Pressure
            _, _, gamma, _, _ = self.propellant.getCombustionProperties(pressure)
            exitPressure = self.nozzle.getExitPressure(gamma, pressure)
            simRes.channels['exitPressure'].addData(exitPressure)

            # Calculate force
            force = self.calcForce(simRes.channels['pressure'].getLast(), dThroat, exitPressure)
            simRes.channels['force'].addData(force)

            simRes.channels['time'].addData(simRes.channels['time'].getLast() + dTime)

            # Calculate any slag deposition or erosion of the throat
            if pressure == 0:
                slagRate = 0
            else:
                slagRate = (1 / pressure) * self.nozzle.getProperty('slagCoeff')
            erosionRate = pressure * self.nozzle.getProperty('erosionCoeff')
            change = dTime * ((-2 * slagRate) + (2 * erosionRate))
            simRes.channels['dThroat'].addData(dThroat + change)

            if callback is not None:
                # Uses the grain with the largest percentage of its web left
                progress = max([g.getWebLeft(r) / g.getWebLeft(0) for g, r in zip(self.grains, perGrainReg)])
                if callback(1 - progress): # If the callback returns true, it is time to cancel
                    return simRes

        simRes.success = True

        if simRes.getPeakMassFlux() > self.config.getProperty('maxMassFlux'):
            desc = 'Peak mass flux exceeded configured limit'
            alert = SimAlert(SimAlertLevel.WARNING, SimAlertType.CONSTRAINT, desc, 'Motor')
            simRes.addAlert(alert)

        if simRes.getMaxPressure() > self.config.getProperty('maxPressure'):
            desc = 'Max pressure exceeded configured limit'
            alert = SimAlert(SimAlertLevel.WARNING, SimAlertType.CONSTRAINT, desc, 'Motor')
            simRes.addAlert(alert)

        # Note that this only adds all errors found on the first datapoint where there were errors to avoid repeating
        # errors. It should be revisited if getPressureErrors ever returns multiple types of errors
        for pressure in simRes.channels['pressure'].getData():
            if pressure > 0:
                err = self.propellant.getPressureErrors(pressure)
                if len(err) > 0:
                    simRes.addAlert(err[0])
                    break

        return simRes
