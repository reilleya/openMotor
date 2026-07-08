import copy

import motorlib

from ..tool import Tool


class NozzleCoeffTool(Tool):
    MAX_ITERATIONS = 10
    CONVERGENCE_THRESHOLD = 0.01  # 1 % relative error on dThroat

    def __init__(self, manager):
        props = {
            'finalDiameter': motorlib.properties.FloatProperty(
                'Post-Fire Throat Diameter', 'm', 0, motorlib.constants.maximumRefDiameter
            ),
            'convergenceThreshold': motorlib.properties.FloatProperty(
                'Convergence Threshold', '%', 0, 100
            )
        }
        props['convergenceThreshold'].setValue(1)
        super().__init__(manager,
                         'Nozzle Erosion/Slag Coefficient',
                         'Use this tool to back-calculate the throat erosion or '
                         'slag buildup coefficient from a measured post-firing '
                         'throat diameter. If the throat grew, the erosion '
                         'coefficient will be set (and slag cleared). If the '
                         'throat shrank, the slag buildup coefficient will be '
                         'set (and erosion cleared).',
                         props,
                         True)

        # Iteration state (all reset at the start of each tool invocation)
        self._iterating = False
        self._targetDThroat = None
        self._currentCoeff = None
        self._isErosion = None
        self._iteration = 0
        self._baseMotor = None  # original motor; receives the final coefficient
        self._convergenceThreshold = self.CONVERGENCE_THRESHOLD

    # ------------------------------------------------------------------
    # Called by the base class after the initial (baseline) simulation
    # ------------------------------------------------------------------
    def applyChanges(self, inp, motor, simulation):
        initialDiameter = motor.nozzle.props['throat'].getValue()
        finalDiameter = inp['finalDiameter']
        dThroat = finalDiameter - initialDiameter

        burnTime = simulation.getBurnTime()
        avgPressure = simulation.getAveragePressure()

        if burnTime == 0 or avgPressure == 0:
            return

        if dThroat == 0:
            motor.nozzle.props['erosionCoeff'].setValue(0)
            motor.nozzle.props['slagCoeff'].setValue(0)
            self.manager.updateMotor(motor)
            return

        isErosion = dThroat > 0

        # Initial coefficient estimate from the unperturbed pressure history.
        # Erosion:  dThroat =  2 * erosionCoeff * P_avg * burnTime
        # Slag:     dThroat = -2 * slagCoeff    * (1/P_avg) * burnTime
        if isErosion:
            coeff = dThroat / (2 * avgPressure * burnTime)
        else:
            coeff = (-dThroat) * avgPressure / (2 * burnTime)

        # Kick off iterative refinement
        self._targetDThroat = dThroat
        self._currentCoeff = coeff
        self._isErosion = isErosion
        self._iteration = 0
        self._baseMotor = motor
        self._convergenceThreshold = inp['convergenceThreshold'] / 100
        self._iterating = True

        self._runIterationSim()

    # ------------------------------------------------------------------
    # Override simDone to intercept iteration simulation results
    # ------------------------------------------------------------------
    def simDone(self, sim):
        if self._iterating:
            self._handleIterationResult(sim)
        else:
            super().simDone(sim)

    def simCanceled(self):
        self._iterating = False
        super().simCanceled()

    # ------------------------------------------------------------------
    # Iteration helpers
    # ------------------------------------------------------------------
    def _runIterationSim(self):
        """Run the motor with the current coefficient estimate."""
        iterMotor = copy.deepcopy(self._baseMotor)
        if self._isErosion:
            iterMotor.nozzle.props['erosionCoeff'].setValue(self._currentCoeff)
            iterMotor.nozzle.props['slagCoeff'].setValue(0)
        else:
            iterMotor.nozzle.props['slagCoeff'].setValue(self._currentCoeff)
            iterMotor.nozzle.props['erosionCoeff'].setValue(0)

        # Run in the background (show=False so the main result view is not updated)
        self.manager.simulationManager.runSimulation(iterMotor, False)

    def _handleIterationResult(self, sim):
        if not sim.success:
            self._iterating = False
            return

        actualDThroat = sim.channels['dThroat'].getLast()
        target = self._targetDThroat
        self._iteration += 1

        # Avoid division by zero if the sim produced no throat change at all
        if actualDThroat == 0:
            self._iterating = False
            return

        relError = abs(actualDThroat - target) / abs(target)

        if relError <= self._convergenceThreshold or self._iteration >= self.MAX_ITERATIONS:
            # Converged (or reached iteration limit) — write to the real motor
            self._iterating = False
            motor = self._baseMotor
            if self._isErosion:
                motor.nozzle.props['erosionCoeff'].setValue(self._currentCoeff)
                motor.nozzle.props['slagCoeff'].setValue(0)
            else:
                motor.nozzle.props['slagCoeff'].setValue(self._currentCoeff)
                motor.nozzle.props['erosionCoeff'].setValue(0)
            self.manager.updateMotor(motor)
        else:
            # Scale coefficient proportionally and iterate
            self._currentCoeff *= target / actualDThroat
            self._runIterationSim()
