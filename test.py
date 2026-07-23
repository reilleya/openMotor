import sys
from scipy.optimize import fsolve

def eRatioFromPRatio(k, pRatio):
    return (((k+1)/2)**(1/(k-1))) * (pRatio ** (1/k)) * ((((k+1)/(k-1))*(1-(pRatio**((k-1)/k))))**0.5)

def getExitPressure(k, inputPressure, expansionRatio):
    if inputPressure == 0:
        return 0
    return fsolve(lambda x: (1/expansionRatio) - eRatioFromPRatio(k, x / inputPressure), 0.0001)[0]

print(getExitPressure(1.2, 3020000, (44.4/21.0)**2))
