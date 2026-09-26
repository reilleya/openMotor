import copy
import tempfile
import unittest
from pathlib import Path

from tools.openmotor_optimizer import (
    apply_variables,
    collect_metrics,
    load_motor,
    numeric_property_paths,
    pareto_front,
    parse_path,
    run_optimization,
)


class FakeResult:

    def getMaxPressure(self):
        return 6e6

    def getAveragePressure(self):
        return 4e6

    def getImpulse(self):
        return 16000

    def getBurnTime(self):
        return 6.5

    def getPropellantMass(self):
        return 12

    def getAverageForce(self):
        return 2400

    def getISP(self):
        return 140

    def getPeakMassFlux(self):
        return 800

    def getPeakMachNumber(self):
        return 0.3

    def getPortRatio(self):
        return 3

    channels = {"force": type("Channel", (), {"getMax": lambda self: 3000})()}


class OptimizerMethods(unittest.TestCase):

    def test_relative_pressure_spread(self):
        metrics = collect_metrics(FakeResult())
        self.assertEqual(metrics["relative_pressure_spread"], 0.5)

    def test_property_paths(self):
        self.assertEqual(
            parse_path("grains[1].properties.length"),
            ["grains", 1, "properties", "length"],
        )
        with self.assertRaises(ValueError):
            parse_path("grains..properties")

    def test_numeric_property_paths(self):
        data = {
            "grains": [
                {
                    "type": "BATES",
                    "properties": {
                        "diameter": 0.1,
                        "numPoints": 6,
                        "inverted": False,
                    },
                }
            ],
            "name": "test",
        }
        self.assertEqual(
            numeric_property_paths(data),
            [
                "grains[0].properties.diameter",
                "grains[0].properties.numPoints",
            ],
        )

    def test_linked_variable_updates_all_paths(self):
        data = {
            "grains": [
                {"properties": {"diameter": 1.0}},
                {"properties": {"diameter": 1.0}},
            ]
        }
        variables = [
            {
                "name": "diameter",
                "paths": [
                    "grains[0].properties.diameter",
                    "grains[1].properties.diameter",
                ],
                "min": 0.5,
                "max": 2.0,
            }
        ]
        updated = apply_variables(data, variables, [1.5])
        self.assertEqual(
            updated["grains"][0]["properties"]["diameter"], 1.5
        )
        self.assertEqual(
            updated["grains"][1]["properties"]["diameter"], 1.5
        )
        self.assertEqual(data["grains"][0]["properties"]["diameter"], 1.0)

    def test_multiobjective_pareto_front(self):
        rows = [
            {
                "candidate": 0,
                "metrics": {"mass": 1.0, "spread": 3.0},
                "feasible": True,
            },
            {
                "candidate": 1,
                "metrics": {"mass": 2.0, "spread": 2.0},
                "feasible": True,
            },
            {
                "candidate": 2,
                "metrics": {"mass": 3.0, "spread": 1.0},
                "feasible": True,
            },
            {
                "candidate": 3,
                "metrics": {"mass": 3.0, "spread": 3.0},
                "feasible": True,
            },
        ]
        objectives = [
            {"metric": "mass", "direction": "minimize"},
            {"metric": "spread", "direction": "minimize"},
        ]
        front = pareto_front(rows, objectives)
        self.assertEqual(
            [row["candidate"] for row in front], [0, 1, 2]
        )

    def test_small_optimization_writes_results(self):
        motorPath = (
            Path(__file__).parents[1]
            / "data"
            / "regression"
            / "simple"
            / "motor.ric"
        )
        motorData, _ = load_motor(motorPath)
        currentLength = motorData["grains"][0]["properties"]["length"]
        with tempfile.TemporaryDirectory() as directory:
            config = {
                "motor": str(motorPath),
                "output_directory": directory,
                "samples": 2,
                "workers": 1,
                "seed": 1,
                "include_current": True,
                "map_dim": 250,
                "validation_map_dim": 250,
                "variables": [
                    {
                        "name": "length",
                        "paths": [
                            "grains[0].properties.length",
                            "grains[1].properties.length",
                        ],
                        "min": currentLength * 0.95,
                        "max": currentLength * 1.05,
                        "type": "float",
                    }
                ],
                "constraints": [],
                "objectives": [
                    {
                        "metric": "propellant_mass",
                        "direction": "minimize",
                    }
                ],
            }
            summary = run_optimization(copy.deepcopy(config))
            self.assertGreater(summary["successful_candidates"], 0)
            self.assertTrue((Path(directory) / "all-results.csv").is_file())
            self.assertTrue((Path(directory) / "summary.json").is_file())
            self.assertTrue(
                (Path(directory) / "minimize_propellant_mass.ric").is_file()
            )


if __name__ == "__main__":
    unittest.main()
