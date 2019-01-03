from . import grain
from . import nozzle
from . import geometry
from . import units

import math

class simulationResult():
    def __init__(self, time, kn, pressure, force, massFlow, massFlux):
        self.time = time
        self.kn = kn
        self.pressure = pressure
        self.force = force
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
        return chr(int(math.log(imp/2.5, 2)) + 66) + str(round(self.getAverageForce()))

    def getPeakMassFlux(self):
        return max([max(mf) for mf in self.massFlux])

class motor():
    def __init__(self):
        self.grains = []
        self.nozzle = nozzle.nozzle()

    def calcKN(self, r):
        surfArea = sum([gr.getSurfaceAreaAtRegression(reg) * int(gr.isWebLeft(reg)) for gr, reg in zip(self.grains, r)])
        nozz = self.nozzle.getThroatArea()
        return surfArea / nozz

    def calcIdealPressure(self, r):
        # Only considers prop from the first grain currently
        k = self.grains[0].props['prop'].getValue()['k']
        t = self.grains[0].props['prop'].getValue()['t']
        m = self.grains[0].props['prop'].getValue()['m']
        p = self.grains[0].props['prop'].getValue()['density']
        a = self.grains[0].props['prop'].getValue()['a']
        n = self.grains[0].props['prop'].getValue()['n']
        num = self.calcKN(r) * p * a
        exponent = 1/(1 - n)
        denom = ((k/((8314/m)*t))*((2/(k+1))**((k+1)/(k-1))))**0.5
        return (num/denom) ** exponent

    def calcForce(self, r):
        # Only considers prop from the first grain currently
        # Assumes full expansion
        p_a = 101353
        p_e = 101353
        p_c = self.calcIdealPressure(r)
        k = self.grains[0].props['prop'].getValue()['k']
        t_a = self.nozzle.getThroatArea()
        e_a = self.nozzle.getExitArea()

        if p_c == 0:
            return 0
 
        t1 = (2*(k**2))/(k-1)
        t2 = (2/(k+1))**((k+1)/(k-1))
        t3 = 1 - ((p_e/p_c) ** ((k-1)/k))

        sr = (t1 * t2 * t3) ** 0.5

        return t_a*p_c*sr + (p_e - p_a) * e_a

    def runSimulation(self):
        burnoutThres = 0.00001
        ts = 0.01

        perGrainReg = [0 for grain in self.grains]

        t = [0, ts]
        k = [0, self.calcKN(perGrainReg)]
        p = [0, self.calcIdealPressure(perGrainReg)]
        f = [0, self.calcForce(perGrainReg)]
        m_flow = [[0, 0] for grain in self.grains]
        m_flux = [[0, 0] for grain in self.grains]

        while any([g.getWebLeft(r) > burnoutThres for g,r in zip(self.grains, perGrainReg)]):
            # Calculate regression
            mf = 0
            for gid, grain in enumerate(self.grains):
                if grain.getWebLeft(perGrainReg[gid]) > burnoutThres:
                    reg = ts * grain.props['prop'].getValue()['a'] * (p[-1]**grain.props['prop'].getValue()['n'])
                    
                    m_flux[gid].append(grain.getPeakMassFlux(mf, ts, perGrainReg[gid], reg))
                    
                    mf += (grain.props['prop'].getValue()['density'] * grain.getVolumeSlice(perGrainReg[gid], reg) / ts)
                    m_flow[gid].append(mf)
                    
                    perGrainReg[gid] += reg

            # Calculate Pressure
            p.append(self.calcIdealPressure(perGrainReg))

            # Calculate force
            f.append(self.calcForce(perGrainReg))

            # Calculate KN
            k.append(self.calcKN(perGrainReg))

            t.append(t[-1] + ts)

        t.append(t[-1] + ts)
        k.append(0)
        p.append(0)
        f.append(0)

        for g in m_flow:
            g.append(0)

        for g in m_flux:
            g.append(0)

        return simulationResult(t, k, p, f, m_flow, m_flux)
