"""
Collection of isolated helper functions extracted from the motor.py.

Purpose: To enforce a clear Separation of Concerns (SRP) and prevent unintended side effects
caused by variable name overlapping/shadowing in nested scopes of the original logic.
"""


def machFunc(
    machNumber: float,
    chamberPressure: float,
    massFlowRation: float,
    gamma: float,
    staticTemperature: float,
    molarMass: float,
    gasConstant: float,
) -> float:
    """Calculates the objective function for finding the Mach number.

    This function represents a rearranged form of the isentropic mass flow equation
    and is designed to be used by a numerical root-finding solver (e.g., Newton's
    method or bisection). The objective is met (returns 0) when the calculated
    mass flow rate equals the given mass_flow_rate.

    Args:
        mach_number: The current Mach number (M) guess for the solver.
        chamber_pressure: The total (stagnation) pressure in the combustion chamber (P0).
        mass_flow_rate: The known, required mass flow rate (m_dot) through the section.
        gamma: The ratio of specific heats (adiabatic index).
        static_temperature: The local static temperature of the gas (T).
        molar_mass: The molar mass of the gas (M_gas).
        universal_gas_constant: The universal gas constant (R).

    Returns:
        The difference between the calculated mass flow rate and the required mass_flow_rate.
        The correct Mach number is found when this value is zero.
    """
    A = chamberPressure * (gamma * molarMass / (gasConstant * staticTemperature)) ** 0.5
    B = 1.0 + ((gamma - 1.0) / 2.0) * machNumber**2
    C = -(gamma + 1.0) / (2.0 * (gamma - 1.0))
    return A * machNumber * (B**C) - massFlowRation


def machFuncDerivative(
    M: float,
    chamberPres: float,
    massFlux: float,
    gamma: float,
    T: float,
    molarMass: float,
    gasConstant,
):
    A = chamberPres * (gamma * molarMass / gasConstant / T) ** 0.5
    B = 1.0 + ((gamma - 1.0) / 2.0) * M**2
    C = -(gamma + 1.0) / (2.0 * (gamma - 1.0))
    dB_dM = (gamma - 1.0) * M
    return A * (B**C + M * C * (B ** (C - 1.0)) * dB_dM)
