"""Module for utils functions to prevent reassign values from an outer scope."""


def machFunc(
    M: float, chamberPres: float, massFlux, gamma, T, molarMass, gasConstant
) -> float:
    A = chamberPres * (gamma * molarMass / (gasConstant * T)) ** 0.5
    B = 1.0 + ((gamma - 1.0) / 2.0) * M**2
    C = -(gamma + 1.0) / (2.0 * (gamma - 1.0))
    return A * M * (B**C) - massFlux


def machFuncDerivative(
    M: float, chamberPres, massFlux, gamma, T, molarMass, gasConstant
):
    A = chamberPres * (gamma * molarMass / gasConstant / T) ** 0.5
    B = 1.0 + ((gamma - 1.0) / 2.0) * M**2
    C = -(gamma + 1.0) / (2.0 * (gamma - 1.0))
    dB_dM = (gamma - 1.0) * M
    return A * (B**C + M * C * (B ** (C - 1.0)) * dB_dM)
