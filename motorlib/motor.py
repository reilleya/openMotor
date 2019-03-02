from . import grain
from . import grainTypes
from . import nozzle
from . import propellant
from . import geometry
from . import units

import math
import numpy as np

class simulationResult():
    def __init__(self, nozzle, grains, time, kn, pressure, force, mass, massFlow, massFlux):
        self.nozzle = nozzle
        self.grains = grains
        self.time = time
        self.kn = kn
        self.pressure = pressure
        self.force = force
        self.mass = mass
        self.massFlow = massFlow
        self.massFlux = massFlux

    def getBurnTime(self):
        return self.time[-1]

    def getInitialKN(self):
        return self.kn[1]

    def getPeakKN(self):
        return max(self.kn)

    def getAveragePressure(self):
        return sum(self.pressure)/len(self.pressure)

    def getMaxPressure(self):
        return max(self.pressure)

    def getImpulse(self):
        impulse = 0
        lastTime = 0
        for time, force in zip(self.time, self.force):
            impulse += force * (time - lastTime)
            lastTime = time
        return impulse

    def getAverageForce(self):
        return sum(self.force)/len(self.force)

    def getDesignation(self):
        imp = self.getImpulse()
        return chr(int(math.log(imp/2.5, 2)) + 66) + str(int(self.getAverageForce()))

    def getPeakMassFlux(self):
        return max([max(mf) for mf in self.massFlux])

    def getISP(self):
        return self.getImpulse() / (sum([grainMass[0] for grainMass in self.mass]) * 9.80665)

    def getPortRatio(self):
        aftPort = self.grains[-1].getPortArea(0)
        if aftPort is not None:
            return aftPort / geometry.circleArea(self.nozzle.props['throat'].getValue())
        else:
            return None

class motor():
    def __init__(self):
        self.grains = []
        self.propellant = propellant()
        self.nozzle = nozzle.nozzle()

    def getDict(self):
        motorData = {}
        motorData['nozzle'] = self.nozzle.getProperties()
        motorData['propellant'] = self.propellant.getProperties()
        motorData['grains'] = [{'type': grain.geomName, 'properties': grain.getProperties()} for grain in self.grains]
        return motorData

    def loadDict(self, dictionary):
        self.nozzle.setProperties(dictionary['nozzle'])
        self.propellant.setProperties(dictionary['propellant'])
        self.grains = []
        for entry in dictionary['grains']:
            self.grains.append(grainTypes[entry['type']]())
            self.grains[-1].setProperties(entry['properties'])

    def calcKN(self, r, burnoutThres = 0.00001):
        surfArea = sum([gr.getSurfaceAreaAtRegression(reg) * int(gr.isWebLeft(reg, burnoutThres)) for gr, reg in zip(self.grains, r)])
        nozz = self.nozzle.getThroatArea()
        return surfArea / nozz

    def calcIdealPressure(self, r, kn = None, burnoutThres = 0.00001):
        k = self.propellant.getProperty('k')
        t = self.propellant.getProperty('t')
        m = self.propellant.getProperty('m')
        p = self.propellant.getProperty('density')
        a = self.propellant.getProperty('a')
        n = self.propellant.getProperty('n')
        if kn is None:
            kn = self.calcKN(r, burnoutThres)
        num = kn * p * a
        exponent = 1/(1 - n)
        denom = ((k/((8314/m)*t))*((2/(k+1))**((k+1)/(k-1))))**0.5
        return (num/denom) ** exponent

    def calcForce(self, r, casePressure = None, ambientPressure = 101325, burnoutThres = 0.00001):
        k = self.propellant.getProperty('k')
        t_a = self.nozzle.getThroatArea()
        e_a = self.nozzle.getExitArea()

        p_a = ambientPressure
        if casePressure is None:
            p_c = self.calcIdealPressure(r, None, burnoutThres)
        else:
            p_c = casePressure

        if p_c == 0:
            return 0
 
        p_e = self.nozzle.getExitPressure(k, p_c)

        t1 = (2*(k**2))/(k-1)
        t2 = (2/(k+1))**((k+1)/(k-1))
        t3 = 1 - ((p_e/p_c) ** ((k-1)/k))

        sr = (t1 * t2 * t3) ** 0.5

        f = self.nozzle.props['efficiency'].getValue()*t_a*p_c*sr + (p_e - p_a) * e_a
        if np.isnan(f):
            f = 0

        return f

    def runSimulation(self, preferences = None):
        if preferences is not None:
            ambientPressure = preferences.general.getProperty('ambPressure')
            burnoutThres = preferences.general.getProperty('burnoutThres')
            ts = preferences.general.getProperty('timestep')

        else:
            ambientPressure = 101325
            burnoutThres = 0.00001
            ts = 0.01

        perGrainReg = [0 for grain in self.grains]

        t = [0, ts]
        k = [0, self.calcKN(perGrainReg, burnoutThres)]
        p = [0, self.calcIdealPressure(perGrainReg, None, burnoutThres)]
        f = [0, self.calcForce(perGrainReg, None, ambientPressure, burnoutThres)]
        mass = [[grain.getVolumeAtRegression(0) * self.propellant.getProperty('density'), grain.getVolumeAtRegression(0) * self.propellant.getProperty('density')] for grain in self.grains]
        m_flow = [[0, 0] for grain in self.grains]
        m_flux = [[0, 0] for grain in self.grains]

        while any([g.getWebLeft(r) > burnoutThres for g,r in zip(self.grains, perGrainReg)]):
            # Calculate regression
            #print(perGrainReg)
            #print([g.getWebLeft(r) for g,r in zip(self.grains, perGrainReg)])
            #print('\n')
            mf = 0
            for gid, grain in enumerate(self.grains):
                if grain.getWebLeft(perGrainReg[gid]) > burnoutThres:
                    reg = ts * self.propellant.getProperty('a') * (p[-1]**self.propellant.getProperty('n'))
                    
                    m_flux[gid].append(grain.getPeakMassFlux(mf, ts, perGrainReg[gid], reg, self.propellant.getProperty('density')))
                    
                    mass[gid].append(grain.getVolumeAtRegression(perGrainReg[gid]) * self.propellant.getProperty('density'))

                    mf += (mass[gid][-1] - mass[gid][-2]) / ts
                    m_flow[gid].append(mf)
                    
                    perGrainReg[gid] += reg

            # Calculate KN
            k.append(self.calcKN(perGrainReg, burnoutThres))

            # Calculate Pressure
            p.append(self.calcIdealPressure(perGrainReg, k[-1], burnoutThres))

            # Calculate force
            f.append(self.calcForce(perGrainReg, p[-1], ambientPressure, burnoutThres))

            t.append(t[-1] + ts)

        t.append(t[-1] + ts)
        k.append(0)
        p.append(0)
        f.append(0)

        for g in mass:
            g.append(0)

        for g in m_flow:
            g.append(0)

        for g in m_flux:
            g.append(0)

        return simulationResult(self.nozzle, self.grains, t, k, p, f, mass, m_flow, m_flux)
