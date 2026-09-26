import math
import unittest

import numpy as np

import motorlib.grains
import motorlib.motor
import motorlib.propellant
from motorlib.simResult import SimAlertLevel


class HemisphericalGrainMethods(unittest.TestCase):

    def setUp(self):
        self.config = motorlib.motor.MotorConfig()
        self.config.setProperty("mapDim", 250)

    def makeTop(self):
        grain = motorlib.grains.TopHemisphericalGrain()
        grain.setProperties({"diameter": 0.1, "portDiameter": 0.04})
        grain.simulationSetup(self.config)
        return grain

    def makeBottom(self):
        grain = motorlib.grains.BottomHemisphericalGrain()
        grain.setProperties(
            {
                "diameter": 0.1,
                "portDiameter": 0.04,
                "outletDiameter": 0.01,
            }
        )
        grain.simulationSetup(self.config)
        return grain

    def test_top_geometry_matches_hemisphere(self):
        grain = self.makeTop()
        outerRadius = 0.05
        portRadius = 0.02
        expectedVolume = (2 / 3) * math.pi * (
            outerRadius**3 - portRadius**3
        )
        expectedArea = 2 * math.pi * portRadius**2

        self.assertAlmostEqual(grain.getProperty("length"), outerRadius)
        self.assertAlmostEqual(
            grain.getGrainBoundingVolume(),
            (2 / 3) * math.pi * outerRadius**3,
        )
        self.assertAlmostEqual(
            grain.getVolumeAtRegression(0), expectedVolume
        )
        self.assertAlmostEqual(
            grain.getSurfaceAreaAtRegression(0),
            expectedArea,
        )
        self.assertIsNone(grain.regressionMap)

    def test_volume_loss_matches_integrated_surface_area(self):
        grain = self.makeTop()
        start = 0.003
        step = 0.000001
        volumeLoss = grain.getVolumeAtRegression(start) - grain.getVolumeAtRegression(
            start + step
        )
        midpointArea = grain.getSurfaceAreaAtRegression(start + step / 2)
        self.assertAlmostEqual(volumeLoss, midpointArea * step, delta=volumeLoss * 1e-8)

    def test_top_area_profile_is_exact_and_smooth(self):
        grain = self.makeTop()
        regressions = np.linspace(0, grain.wallWeb * 0.99, 500)
        expectedAreas = 2 * math.pi * (0.02 + regressions) ** 2
        actualAreas = np.array(
            [grain.getSurfaceAreaAtRegression(reg) for reg in regressions]
        )
        np.testing.assert_allclose(actualAreas, expectedAreas, rtol=1e-12)

    def test_bottom_area_matches_volume_derivative(self):
        grain = self.makeBottom()
        regressions = np.linspace(
            grain.wallWeb * 0.01, grain.wallWeb * 0.99, 300
        )
        step = grain.wallWeb * 1e-5
        areas = np.array(
            [grain.getSurfaceAreaAtRegression(reg) for reg in regressions]
        )
        volumeDerivatives = np.array(
            [
                (
                    grain.getVolumeAtRegression(reg - step)
                    - grain.getVolumeAtRegression(reg + step)
                )
                / (2 * step)
                for reg in regressions
            ]
        )
        np.testing.assert_allclose(areas, volumeDerivatives, rtol=1e-7)

    def test_bottom_has_open_outlet(self):
        top = self.makeTop()
        bottom = self.makeBottom()
        self.assertLess(
            bottom.getVolumeAtRegression(0), top.getVolumeAtRegression(0)
        )
        self.assertAlmostEqual(
            bottom.getPortArea(0), math.pi * (0.01 / 2) ** 2
        )
        self.assertGreater(
            bottom.getSurfaceAreaAtRegression(0),
            top.getSurfaceAreaAtRegression(0),
        )

    def test_capsule_placement(self):
        motor = motorlib.motor.Motor()
        top = self.makeTop()
        middle = motorlib.grains.BatesGrain()
        middle.setProperties(
            {
                "diameter": 0.1,
                "length": 0.1,
                "coreDiameter": 0.04,
                "inhibitedEnds": "Both",
            }
        )
        middle.simulationSetup(self.config)
        bottom = self.makeBottom()
        motor.grains = [top, middle, bottom]

        errors = [
            alert
            for alert in motor.getCapsulePlacementErrors(checkInterfaces=True)
            if alert.level == SimAlertLevel.ERROR
        ]
        self.assertEqual(errors, [])

        motor.grains = [middle, top, bottom]
        errors = [
            alert
            for alert in motor.getCapsulePlacementErrors()
            if alert.level == SimAlertLevel.ERROR
        ]
        self.assertGreater(len(errors), 0)

    def test_capsule_ends_are_independent(self):
        motor = motorlib.motor.Motor()
        middle = motorlib.grains.BatesGrain()
        middle.setProperties(
            {
                "diameter": 0.1,
                "length": 0.1,
                "coreDiameter": 0.04,
                "inhibitedEnds": "Top",
            }
        )
        motor.grains = [self.makeTop(), middle]
        topErrors = [
            alert
            for alert in motor.getCapsulePlacementErrors()
            if alert.level == SimAlertLevel.ERROR
        ]
        self.assertEqual(topErrors, [])

        middle.setProperty("inhibitedEnds", "Bottom")
        motor.grains = [middle, self.makeBottom()]
        bottomErrors = [
            alert
            for alert in motor.getCapsulePlacementErrors()
            if alert.level == SimAlertLevel.ERROR
        ]
        self.assertEqual(bottomErrors, [])

    def test_bottom_outlet_may_exceed_mating_port(self):
        grain = motorlib.grains.BottomHemisphericalGrain()
        grain.setProperties(
            {
                "diameter": 0.1,
                "portDiameter": 0.02,
                "outletDiameter": 0.04,
            }
        )
        self.assertEqual(grain.getGeometryErrors(), [])
        grain.simulationSetup(self.config)
        self.assertGreater(grain.getPortArea(0), grain.getMatingPortArea(0))

    def test_capsule_round_trip(self):
        motor = motorlib.motor.Motor()
        top = self.makeTop()
        middle = motorlib.grains.BatesGrain()
        middle.setProperties(
            {
                "diameter": 0.1,
                "length": 0.1,
                "coreDiameter": 0.04,
                "inhibitedEnds": "Both",
            }
        )
        bottom = self.makeBottom()
        motor.grains = [top, middle, bottom]

        restored = motorlib.motor.Motor(motor.getDict())
        self.assertIsInstance(
            restored.grains[0], motorlib.grains.TopHemisphericalGrain
        )
        self.assertIsInstance(
            restored.grains[-1], motorlib.grains.BottomHemisphericalGrain
        )
        self.assertEqual(restored.grains[0].getProperty("length"), 0.05)
        self.assertEqual(restored.grains[-1].getProperty("outletDiameter"), 0.01)

    def test_regression_preview_data(self):
        grain = self.makeBottom()
        face, regression, contours, surfaceAreas = grain.getRegressionData(
            128, numContours=5
        )
        self.assertEqual(face.shape, (128, 256))
        self.assertEqual(regression.shape, (128, 256))
        self.assertEqual(len(contours), 5)
        self.assertEqual(len(surfaceAreas), 5)

    def test_capsule_simulation(self):
        motor = motorlib.motor.Motor()
        motor.config.setProperties(
            {
                "mapDim": 250,
                "timestep": 0.005,
                "burnoutWebThres": 0.00025,
                "burnoutThrustThres": 0.1,
                "ambPressure": 101325,
                "maxPressure": 7e7,
                "maxMassFlux": 1e4,
                "maxMachNumber": 1,
                "minPortThroat": 2,
                "flowSeparationWarnPercent": 1,
                "sepPressureRatio": 0.4,
            }
        )
        top = motorlib.grains.TopHemisphericalGrain()
        top.setProperties({"diameter": 0.083, "portDiameter": 0.025})
        middle = motorlib.grains.BatesGrain()
        middle.setProperties(
            {
                "diameter": 0.083,
                "length": 0.12,
                "coreDiameter": 0.025,
                "inhibitedEnds": "Both",
            }
        )
        bottom = motorlib.grains.BottomHemisphericalGrain()
        bottom.setProperties(
            {
                "diameter": 0.083,
                "portDiameter": 0.025,
                "outletDiameter": 0.016,
            }
        )
        motor.grains = [top, middle, bottom]
        motor.nozzle.setProperties(
            {
                "throat": 0.008,
                "exit": 0.018,
                "efficiency": 0.9,
                "divAngle": 15,
                "convAngle": 45,
                "throatLength": 0.01,
                "erosionCoeff": 0,
                "slagCoeff": 0,
            }
        )
        motor.propellant = motorlib.propellant.Propellant(
            {
                "name": "Test propellant",
                "density": 1800,
                "tabs": [
                    {
                        "minPressure": 0,
                        "maxPressure": 7e7,
                        "a": 0.00001,
                        "n": 0.35,
                        "k": 1.2,
                        "t": 1700,
                        "m": 40,
                    }
                ],
            }
        )

        result = motor.runSimulation()
        self.assertTrue(result.success)
        self.assertGreater(result.getImpulse(), 0)

        pressure = np.asarray(result.channels["pressure"].getData())
        edge = len(pressure) // 10
        activePressure = pressure[edge:-edge]
        normalizedCurvature = (
            np.sqrt(np.mean(np.diff(activePressure, n=2) ** 2))
            / np.mean(activePressure)
        )
        self.assertLess(normalizedCurvature, 1e-5)


if __name__ == "__main__":
    unittest.main()
