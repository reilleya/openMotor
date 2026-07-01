import sys
import subprocess
import math

# --- Dependency Installation ---
def install_dependencies():
    packages = ["numpy", "scipy", "matplotlib"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} modülü bulunamadı, yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import numpy as np
from scipy.optimize import fsolve, newton
import matplotlib.pyplot as plt

# --- Constants ---
GAS_CONSTANT = 8314.462618
ATMOSPHERIC_PRESSURE = 101325
STANDARD_GRAVITY = 9.80665

# --- Mathematical Functions (from geometry.py and nozzle.py) ---
def circleArea(dia: float) -> float:
    return ((dia / 2) ** 2) * math.pi

def circlePerimeter(dia: float) -> float:
    return dia * math.pi

def cylinderVolume(dia: float, height: float) -> float:
    return height * circleArea(dia)

def eRatioFromPRatio(k: float, pRatio: float) -> float:
    return (((k+1)/2)**(1/(k-1))) * (pRatio ** (1/k)) * ((((k+1)/(k-1))*(1-(pRatio**((k-1)/k))))**0.5)

# --- Classes ---

class Propellant:
    def __init__(self, density: float, a: float, n: float, k: float, t: float, m: float):
        self.density = density
        self.a = a
        self.n = n
        self.k = k
        self.t = t
        self.m = m # g/mol

    def getCombustionProperties(self):
        return self.a, self.n, self.k, self.t, self.m

    def getBurnRate(self, pressure: float) -> float:
        return self.a * (pressure ** self.n)

    def getPressureFromKn(self, kn: float) -> float:
        num = kn * self.density * self.a
        exponent = 1 / (1 - self.n)
        denom = ((self.k / ((GAS_CONSTANT / self.m) * self.t)) * ((2 / (self.k + 1)) ** ((self.k + 1) / (self.k - 1)))) ** 0.5
        return (num / denom) ** exponent

class Nozzle:
    def __init__(self, throat_dia: float, exit_dia: float, efficiency: float, div_angle_deg: float):
        self.throat_dia = throat_dia
        self.exit_dia = exit_dia
        self.efficiency = efficiency
        self.div_angle_deg = div_angle_deg

        # Fixed assumptions:
        self.throatLength = throat_dia / 2.0  # Assumed throat aspect

    def calcExpansion(self) -> float:
        return (self.exit_dia / self.throat_dia) ** 2

    def getThroatArea(self) -> float:
        return circleArea(self.throat_dia)

    def getExitArea(self) -> float:
        return circleArea(self.exit_dia)

    def getExitPressure(self, k: float, inputPressure: float) -> float:
        if inputPressure == 0:
            return 0
        expansion = self.calcExpansion()
        def func(x):
            return (1/expansion) - eRatioFromPRatio(k, x / inputPressure)
        try:
            return fsolve(func, 0.0001)[0]
        except:
            return 0

    def getDivergenceLosses(self) -> float:
        divAngleRad = math.radians(self.div_angle_deg)
        return (1 + math.cos(divAngleRad)) / 2

    def getThroatLosses(self) -> float:
        throatAspect = self.throatLength / self.throat_dia
        if throatAspect > 0.45:
            return 0.95
        return 0.99 - (0.0333 * throatAspect)

    def getSkinLosses(self) -> float:
        return 0.99

    def getIdealThrustCoeff(self, chamberPres: float, ambPres: float, gamma: float, exitPres: float = None) -> float:
        if chamberPres == 0:
            return 0
        if exitPres is None:
            exitPres = self.getExitPressure(gamma, chamberPres)

        exitArea = self.getExitArea()
        throatArea = self.getThroatArea()

        term1 = (2 * (gamma ** 2)) / (gamma - 1)
        term2 = (2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1))
        # Protect against negative base in exponent if exitPres > chamberPres
        p_ratio = max(0, min(1.0, exitPres / chamberPres))
        term3 = 1 - (p_ratio ** ((gamma - 1) / gamma))

        momentumThrust = (term1 * term2 * term3) ** 0.5
        pressureThrust = ((exitPres - ambPres) * exitArea) / (throatArea * chamberPres)

        return momentumThrust + pressureThrust

    def getAdjustedThrustCoeff(self, chamberPres: float, ambPres: float, gamma: float, exitPres: float = None) -> float:
        thrustCoeffIdeal = self.getIdealThrustCoeff(chamberPres, ambPres, gamma, exitPres)
        divLoss = self.getDivergenceLosses()
        throatLoss = self.getThroatLosses()
        skinLoss = self.getSkinLosses()
        return divLoss * throatLoss * self.efficiency * (skinLoss * thrustCoeffIdeal + (1 - skinLoss))

class BatesGrain:
    def __init__(self, outer_dia: float, core_dia: float, length: float):
        self.outer_dia = outer_dia
        self.core_dia = core_dia
        self.length = length
        self.wallWeb = (outer_dia - core_dia) / 2.0

    def getEndPositions(self, regDist: float):
        # Uninhibited (Both Ends)
        return (regDist, self.length - regDist)

    def getRegressedLength(self, regDist: float) -> float:
        endPos = self.getEndPositions(regDist)
        return endPos[1] - endPos[0]

    def getWebLeft(self, regDist: float) -> float:
        wallLeft = self.wallWeb - regDist
        lengthLeft = self.getRegressedLength(regDist)
        return min(lengthLeft, wallLeft)

    def getFaceArea(self, regDist: float) -> float:
        outer = circleArea(self.outer_dia)
        inner = circleArea(self.core_dia + (2 * regDist))
        return outer - inner

    def getCoreSurfaceArea(self, regDist: float) -> float:
        curLength = self.getRegressedLength(regDist)
        curCoreDia = self.core_dia + (2 * regDist)
        return curCoreDia * math.pi * curLength

    def getSurfaceAreaAtRegression(self, regDist: float) -> float:
        faceArea = self.getFaceArea(regDist)
        coreArea = self.getCoreSurfaceArea(regDist)
        exposedFaces = 2 # Uninhibited
        return coreArea + (exposedFaces * faceArea)

    def getVolumeAtRegression(self, regDist: float) -> float:
        faceArea = self.getFaceArea(regDist)
        return faceArea * self.getRegressedLength(regDist)

    def getGrainBoundingVolume(self) -> float:
        return cylinderVolume(self.outer_dia, self.length)

    def getFreeVolume(self, regDist: float) -> float:
        return self.getGrainBoundingVolume() - self.getVolumeAtRegression(regDist)

class Motor:
    def __init__(self, num_grains: int, bates_grain: BatesGrain, nozzle: Nozzle, propellant: Propellant):
        self.grains = [BatesGrain(bates_grain.outer_dia, bates_grain.core_dia, bates_grain.length) for _ in range(num_grains)]
        self.nozzle = nozzle
        self.propellant = propellant

    def calcBurningSurfaceArea(self, perGrainReg: list) -> float:
        burnoutThres = 2.54e-5
        totalArea = 0
        for gr, reg in zip(self.grains, perGrainReg):
            if gr.getWebLeft(reg) > burnoutThres:
                totalArea += gr.getSurfaceAreaAtRegression(reg)
        return totalArea

    def calcKN(self, perGrainReg: list) -> float:
        burningSurfaceArea = self.calcBurningSurfaceArea(perGrainReg)
        nozzleArea = self.nozzle.getThroatArea()
        return burningSurfaceArea / nozzleArea

    def calcIdealPressure(self, perGrainReg: list, kn: float = None) -> float:
        if kn is None:
            kn = self.calcKN(perGrainReg)
        if kn <= 0:
            return 0
        return self.propellant.getPressureFromKn(kn)

    def calcForce(self, chamberPres: float, exitPres: float = None) -> float:
        if chamberPres <= ATMOSPHERIC_PRESSURE:
            return 0
        a, n, gamma, t, m = self.propellant.getCombustionProperties()
        thrustCoeff = self.nozzle.getAdjustedThrustCoeff(chamberPres, ATMOSPHERIC_PRESSURE, gamma, exitPres)
        thrust = thrustCoeff * self.nozzle.getThroatArea() * chamberPres
        return max(thrust, 0)

def get_float_input(prompt: str, default: float = None) -> float:
    while True:
        try:
            val = input(prompt)
            if not val and default is not None:
                return default
            return float(val)
        except ValueError:
            print("Lütfen geçerli bir sayı giriniz.")

def get_int_input(prompt: str, default: int = None) -> int:
    while True:
        try:
            val = input(prompt)
            if not val and default is not None:
                return default
            return int(val)
        except ValueError:
            print("Lütfen geçerli bir tam sayı giriniz.")

def run_simulation():
    print("=== openMotor BATES İtki-Zaman Grafiği Çizici ===")
    print("Lütfen değerleri istenen birimlerde giriniz. (Varsayılan değerleri parantez içinde görebilirsiniz)")
    print("\n--- Yakıt (Propellant) Özellikleri ---")
    density = get_float_input("Yoğunluk (Density) [kg/m³] (örn: 1548): ", 1548.0)
    a = get_float_input("Yanma Hızı Katsayısı (a) [m/(s·Paⁿ)] (örn: 0.0000353): ", 0.0000353)
    n = get_float_input("Yanma Hızı Üssü (n) (örn: 0.245): ", 0.245)
    k = get_float_input("Özgül Isı Oranı (k/gamma) (örn: 1.045): ", 1.045)
    t = get_float_input("Yanma Sıcaklığı (T) [K] (örn: 1584): ", 1584.0)
    m = get_float_input("Egzoz Molar Kütlesi (M) [g/mol] (örn: 38.61): ", 38.61)

    print("\n--- Nozul (Nozzle) Özellikleri ---")
    throat_dia_mm = get_float_input("Nozul Boğaz Çapı [mm] (örn: 12.7): ", 12.7)
    exit_dia_mm = get_float_input("Nozul Çıkış Çapı [mm] (örn: 25.4): ", 25.4)
    efficiency = get_float_input("Nozul Verimi [örn: 0.95]: ", 0.95)
    div_angle = get_float_input("Nozul Ayrılma Açısı (Divergence Half Angle) [Derece] (örn: 15): ", 15.0)

    print("\n--- BATES Yakıt (Grain) Boyutları ---")
    num_grains = get_int_input("Grain (Yakıt Bloğu) Adedi (örn: 3): ", 3)
    outer_dia_mm = get_float_input("Grain Dış Çapı [mm] (örn: 38.1): ", 38.1)
    core_dia_mm = get_float_input("Grain İç Çapı (Core) [mm] (örn: 12.7): ", 12.7)
    length_mm = get_float_input("Grain Boyu (Length) [mm] (örn: 76.2): ", 76.2)

    timestep = get_float_input("Simülasyon Zaman Adımı (Timestep) [s] (örn: 0.01): ", 0.01)

    # Unit conversions
    throat_dia = throat_dia_mm / 1000.0
    exit_dia = exit_dia_mm / 1000.0
    outer_dia = outer_dia_mm / 1000.0
    core_dia = core_dia_mm / 1000.0
    length = length_mm / 1000.0

    # Initialize objects
    prop = Propellant(density, a, n, k, t, m)
    noz = Nozzle(throat_dia, exit_dia, efficiency, div_angle)
    bates = BatesGrain(outer_dia, core_dia, length)
    motor = Motor(num_grains, bates, noz, prop)

    # Sim parameters
    burnoutWebThres = 2.54e-5
    perGrainReg = [0.0 for _ in range(num_grains)]

    times = []
    thrusts = []
    pressures = []

    current_time = 0.0

    # Initial state
    kn = motor.calcKN(perGrainReg)
    pressure = motor.calcIdealPressure(perGrainReg, kn)
    force = motor.calcForce(pressure)

    times.append(current_time)
    thrusts.append(force)
    pressures.append(pressure)

    print("\nSimülasyon çalışıyor...")

    while True:
        # Calculate Regression
        active_grains = False
        perGrainRegNext = list(perGrainReg)

        for gid in range(num_grains):
            grain = motor.grains[gid]
            if grain.getWebLeft(perGrainReg[gid]) > burnoutWebThres:
                active_grains = True
                reg = timestep * prop.getBurnRate(pressure)
                perGrainRegNext[gid] += reg

        if not active_grains:
            break

        perGrainReg = perGrainRegNext

        # Update values
        kn = motor.calcKN(perGrainReg)
        pressure = motor.calcIdealPressure(perGrainReg, kn)

        _, _, gamma, _, _ = prop.getCombustionProperties()
        exitPressure = noz.getExitPressure(gamma, pressure)
        force = motor.calcForce(pressure, exitPressure)

        current_time += timestep

        times.append(current_time)
        thrusts.append(force)
        pressures.append(pressure)

        if force < 0.1 and active_grains is False:
             break
        if pressure < ATMOSPHERIC_PRESSURE and active_grains is False:
             break

    print("Simülasyon tamamlandı. Grafik çiziliyor...")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(times, thrusts, label="İtki (Thrust) [N]", color="red", linewidth=2)
    plt.title("openMotor - BATES İtki Zaman Grafiği")
    plt.xlabel("Zaman [s]")
    plt.ylabel("İtki [N]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()
