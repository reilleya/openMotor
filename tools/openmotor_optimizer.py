"""Configurable multi-objective optimizer for openMotor motor files."""

import argparse
import copy
import csv
import json
import math
import os
import re
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import yaml
from matplotlib.figure import Figure
from scipy.stats import qmc

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from motorlib.motor import Motor


PATH_TOKEN = re.compile(r"([^.[]+)|\[(\d+)\]")
VALID_PATH = re.compile(
    r"^[A-Za-z_][^.[]*(?:\[\d+\])?"
    r"(?:\.[A-Za-z_][^.[]*(?:\[\d+\])?)*$"
)
METRIC_UNITS = {
    "impulse": "N s",
    "burn_time": "s",
    "peak_pressure": "Pa",
    "average_pressure": "Pa",
    "pressure_spread": "Pa",
    "relative_pressure_spread": "",
    "propellant_mass": "kg",
    "average_thrust": "N",
    "peak_thrust": "N",
    "specific_impulse": "s",
    "peak_mass_flux": "kg/(m^2 s)",
    "peak_mach": "",
    "port_throat_ratio": "",
}

_workerData = None
_workerVariables = None
_workerConstraints = None
_workerMapDim = None


def parse_path(path):
    """Convert a path such as grains[0].properties.length into tokens."""
    if not VALID_PATH.fullmatch(path):
        raise ValueError(f"Invalid property path: {path}")
    tokens = []
    for name, index in PATH_TOKEN.findall(path):
        tokens.append(int(index) if index else name)
    return tokens


def get_path(data, path):
    value = data
    for token in parse_path(path):
        value = value[token]
    return value


def set_path(data, path, value):
    tokens = parse_path(path)
    target = data
    for token in tokens[:-1]:
        target = target[token]
    target[tokens[-1]] = value


def numeric_property_paths(data, prefix=""):
    """Return sorted paths for all numeric values in a motor dictionary."""
    paths = []
    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            paths.extend(numeric_property_paths(value, path))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            paths.extend(
                numeric_property_paths(value, f"{prefix}[{index}]")
            )
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        paths.append(prefix)
    return sorted(paths)


def load_motor(path):
    """Load the data and serialization trailer from an openMotor file."""
    text = Path(path).read_text(encoding="utf-8")
    body, separator, trailer = text.partition("\ntype:")
    if not separator:
        raise ValueError(f"{path} is missing the openMotor file type")
    document = yaml.safe_load(body)
    if not isinstance(document, dict) or "data" not in document:
        raise ValueError(f"{path} does not contain motor data")
    return document["data"], trailer


def save_motor(path, data, trailer):
    content = yaml.safe_dump(
        {"data": data}, sort_keys=False, default_flow_style=False
    )
    Path(path).write_text(content + "type:" + trailer, encoding="utf-8")


def load_config(path):
    configPath = Path(path).resolve()
    config = yaml.safe_load(configPath.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Optimizer configuration must be a YAML mapping")

    for field in ("motor", "variables", "constraints", "objectives"):
        if field not in config:
            raise ValueError(f"Missing required configuration field: {field}")

    base = configPath.parent
    motorPath = Path(config["motor"])
    outputPath = Path(config.get("output_directory", "optimization-results"))
    if not motorPath.is_absolute():
        motorPath = base / motorPath
    if not outputPath.is_absolute():
        outputPath = base / outputPath
    config["motor"] = str(motorPath.resolve())
    config["output_directory"] = str(outputPath.resolve())
    validate_config(config)
    return config


def validate_config(config):
    if not Path(config["motor"]).is_file():
        raise ValueError(f"Motor file does not exist: {config['motor']}")
    if not config["variables"]:
        raise ValueError("At least one optimization variable is required")
    if not config["objectives"]:
        raise ValueError("At least one objective is required")

    motorData, _ = load_motor(config["motor"])
    names = set()
    for variable in config["variables"]:
        for field in ("name", "paths", "min", "max"):
            if field not in variable:
                raise ValueError(
                    f"Variable is missing required field: {field}"
                )
        if variable["name"] in names:
            raise ValueError(f"Duplicate variable name: {variable['name']}")
        names.add(variable["name"])
        if variable["min"] >= variable["max"]:
            raise ValueError(
                f"{variable['name']} must have min less than max"
            )
        paths = variable["paths"]
        if isinstance(paths, str):
            paths = [paths]
            variable["paths"] = paths
        if not paths:
            raise ValueError(f"{variable['name']} has no property paths")
        for path in paths:
            value = get_path(motorData, path)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{path} does not point to a number")
        valueType = variable.get("type", "float")
        if valueType not in ("float", "integer"):
            raise ValueError(
                f"{variable['name']} type must be float or integer"
            )

    for constraint in config["constraints"]:
        _validate_metric_spec(constraint, "constraint")
        if "min" not in constraint and "max" not in constraint:
            raise ValueError(
                f"Constraint {constraint['metric']} needs min or max"
            )
    for objective in config["objectives"]:
        _validate_metric_spec(objective, "objective")
        if objective.get("direction", "minimize") not in (
            "minimize",
            "maximize",
        ):
            raise ValueError(
                f"Invalid direction for {objective['metric']}"
            )

    samples = int(config.get("samples", 2000))
    if samples < 1:
        raise ValueError("samples must be at least 1")
    workers = int(config.get("workers", max(1, (os.cpu_count() or 2) - 1)))
    if workers < 1:
        raise ValueError("workers must be at least 1")


def _validate_metric_spec(spec, kind):
    if "metric" not in spec:
        raise ValueError(f"Each {kind} requires a metric")
    if spec["metric"] not in METRIC_UNITS:
        raise ValueError(f"Unknown metric: {spec['metric']}")


def apply_variables(data, variables, values):
    candidate = copy.deepcopy(data)
    for variable, rawValue in zip(variables, values):
        value = (
            int(round(rawValue))
            if variable.get("type", "float") == "integer"
            else float(rawValue)
        )
        for path in variable["paths"]:
            set_path(candidate, path, value)
    return candidate


def collect_metrics(result):
    peakPressure = result.getMaxPressure()
    averagePressure = result.getAveragePressure()
    relativePressureSpread = (
        (peakPressure - averagePressure) / averagePressure
        if averagePressure > 0
        else math.inf
    )
    return {
        "impulse": result.getImpulse(),
        "burn_time": result.getBurnTime(),
        "peak_pressure": peakPressure,
        "average_pressure": averagePressure,
        "pressure_spread": peakPressure - averagePressure,
        "relative_pressure_spread": relativePressureSpread,
        "propellant_mass": result.getPropellantMass(),
        "average_thrust": result.getAverageForce(),
        "peak_thrust": result.channels["force"].getMax(),
        "specific_impulse": result.getISP(),
        "peak_mass_flux": result.getPeakMassFlux(),
        "peak_mach": result.getPeakMachNumber(),
        "port_throat_ratio": result.getPortRatio(),
    }


def is_feasible(metrics, constraints):
    for constraint in constraints:
        value = metrics.get(constraint["metric"])
        if value is None or not math.isfinite(value):
            return False
        if "min" in constraint and value < constraint["min"]:
            return False
        if "max" in constraint and value > constraint["max"]:
            return False
    return True


def _evaluate(data, variables, values, constraints, mapDim):
    candidateData = apply_variables(data, variables, values)
    if mapDim is not None:
        candidateData["config"]["mapDim"] = mapDim
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = Motor(candidateData).runSimulation()
        if not result.success or not result.channels["time"].data:
            return None
        metrics = collect_metrics(result)
        return metrics, is_feasible(metrics, constraints)
    except (ArithmeticError, RuntimeError, TypeError, ValueError):
        return None


def _initialize_worker(data, variables, constraints, mapDim):
    global _workerData
    global _workerVariables
    global _workerConstraints
    global _workerMapDim
    _workerData = data
    _workerVariables = variables
    _workerConstraints = constraints
    _workerMapDim = mapDim


def _evaluate_worker(item):
    index, values = item
    evaluation = _evaluate(
        _workerData,
        _workerVariables,
        values,
        _workerConstraints,
        _workerMapDim,
    )
    if evaluation is None:
        return None
    metrics, feasible = evaluation
    return {
        "candidate": index,
        "values": [float(value) for value in values],
        "metrics": metrics,
        "feasible": feasible,
    }


def candidate_values(config, motorData):
    variables = config["variables"]
    lower = np.array([variable["min"] for variable in variables], dtype=float)
    upper = np.array([variable["max"] for variable in variables], dtype=float)
    samples = int(config.get("samples", 2000))
    sampler = qmc.LatinHypercube(
        d=len(variables), seed=int(config.get("seed", 1))
    )
    values = qmc.scale(sampler.random(samples), lower, upper)
    for index, variable in enumerate(variables):
        if variable.get("type", "float") == "integer":
            values[:, index] = np.rint(values[:, index])

    if config.get("include_current", True):
        current = np.array(
            [get_path(motorData, variable["paths"][0]) for variable in variables],
            dtype=float,
        )
        values = np.vstack((current, values))
    return values


def pareto_front(rows, objectives):
    feasible = [
        row
        for row in rows
        if row["feasible"]
        and all(
            row["metrics"].get(objective["metric"]) is not None
            and math.isfinite(row["metrics"][objective["metric"]])
            for objective in objectives
        )
    ]
    values = np.asarray(
        [_oriented_objectives(row, objectives) for row in feasible],
        dtype=float,
    )
    dominated = np.zeros(len(feasible), dtype=bool)
    for index, candidateValues in enumerate(values):
        noWorse = np.all(values <= candidateValues, axis=1)
        strictlyBetter = np.any(values < candidateValues, axis=1)
        dominated[index] = np.any(noWorse & strictlyBetter)
    front = [
        row for row, isDominated in zip(feasible, dominated) if not isDominated
    ]
    return sorted(
        front,
        key=lambda row: tuple(_oriented_objectives(row, objectives)),
    )


def _oriented_objectives(row, objectives):
    return [
        row["metrics"][objective["metric"]]
        * (-1 if objective.get("direction", "minimize") == "maximize" else 1)
        for objective in objectives
    ]


def select_cases(front, objectives):
    selected = {}
    for objective in objectives:
        metric = objective["metric"]
        reverse = objective.get("direction", "minimize") == "maximize"
        selected[f"{objective.get('direction', 'minimize')}_{metric}"] = (
            max(front, key=lambda row: row["metrics"][metric])
            if reverse
            else min(front, key=lambda row: row["metrics"][metric])
        )

    if len(objectives) > 1:
        objectiveMatrix = np.asarray(
            [_oriented_objectives(row, objectives) for row in front],
            dtype=float,
        )
        minimums = objectiveMatrix.min(axis=0)
        spans = np.ptp(objectiveMatrix, axis=0)
        spans[spans == 0] = 1
        distances = np.linalg.norm(
            (objectiveMatrix - minimums) / spans, axis=1
        )
        selected["balanced"] = front[int(np.argmin(distances))]
    return selected


def _result_row(row, variables):
    output = {
        "candidate": row["candidate"],
        "feasible": row["feasible"],
    }
    output.update(
        {
            variable["name"]: value
            for variable, value in zip(variables, row["values"])
        }
    )
    output.update(row["metrics"])
    return output


def _save_csv(path, rows, variables):
    flattened = [_result_row(row, variables) for row in rows]
    with Path(path).open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(flattened[0]))
        writer.writeheader()
        writer.writerows(flattened)


def _save_pareto_plot(path, front, objectives, selected):
    if len(objectives) < 2:
        return
    xMetric = objectives[0]["metric"]
    yMetric = objectives[1]["metric"]
    figure = Figure(figsize=(8, 6))
    axis = figure.subplots()
    axis.scatter(
        [row["metrics"][xMetric] for row in front],
        [row["metrics"][yMetric] for row in front],
        s=18,
        alpha=0.7,
        label="Pareto front",
    )
    for label, row in selected.items():
        axis.scatter(
            row["metrics"][xMetric],
            row["metrics"][yMetric],
            s=65,
            label=label.replace("_", " ").title(),
        )
    axis.set_xlabel(f"{xMetric} ({METRIC_UNITS[xMetric]})")
    axis.set_ylabel(f"{yMetric} ({METRIC_UNITS[yMetric]})")
    axis.grid(True, alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=180)


def _save_pressure_plot(path, motorData, trailer, variables, selected):
    del trailer
    figure = Figure(figsize=(9, 6))
    axis = figure.subplots()
    for label, row in selected.items():
        candidateData = apply_variables(motorData, variables, row["values"])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = Motor(candidateData).runSimulation()
        axis.plot(
            result.channels["time"].getData(),
            np.asarray(result.channels["pressure"].getData()) / 1e6,
            label=label.replace("_", " ").title(),
        )
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Chamber pressure (MPa)")
    axis.grid(True, alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=180)


def _validate_selected(
    selected, motorData, variables, constraints, validationMapDim
):
    validated = {}
    for label, row in selected.items():
        evaluation = _evaluate(
            motorData,
            variables,
            row["values"],
            constraints,
            validationMapDim,
        )
        if evaluation is None:
            raise RuntimeError(f"Validation failed for {label}")
        metrics, feasible = evaluation
        if not feasible:
            raise RuntimeError(
                f"{label} does not satisfy constraints during validation"
            )
        validated[label] = {
            **row,
            "metrics": metrics,
            "feasible": True,
        }
    return validated


def save_outputs(config, motorData, trailer, rows, front, selected):
    outputDirectory = Path(config["output_directory"])
    outputDirectory.mkdir(parents=True, exist_ok=True)
    variables = config["variables"]

    _save_csv(outputDirectory / "all-results.csv", rows, variables)
    _save_csv(outputDirectory / "pareto-front.csv", front, variables)
    summary = {
        "successful_candidates": len(rows),
        "feasible_candidates": sum(row["feasible"] for row in rows),
        "pareto_candidates": len(front),
        "selected": {
            label: _result_row(row, variables)
            for label, row in selected.items()
        },
    }
    (outputDirectory / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    for label, row in selected.items():
        data = apply_variables(motorData, variables, row["values"])
        save_motor(outputDirectory / f"{label}.ric", data, trailer)

    _save_pareto_plot(
        outputDirectory / "pareto-front.png",
        front,
        config["objectives"],
        selected,
    )
    _save_pressure_plot(
        outputDirectory / "pressure-comparison.png",
        motorData,
        trailer,
        variables,
        selected,
    )
    return summary


def run_optimization(config, progress=None):
    """Run an optimization and return its saved summary."""
    validate_config(config)
    motorData, trailer = load_motor(config["motor"])
    values = candidate_values(config, motorData)
    workers = min(
        int(config.get("workers", max(1, (os.cpu_count() or 2) - 1))),
        len(values),
    )
    mapDim = config.get("map_dim")
    if mapDim is not None:
        mapDim = int(mapDim)

    if progress:
        progress("Evaluating candidates", 0, len(values))
    rows = []
    items = list(enumerate(values))
    if workers == 1:
        _initialize_worker(
            motorData, config["variables"], config["constraints"], mapDim
        )
        iterator = map(_evaluate_worker, items)
        executor = None
    else:
        executor = ProcessPoolExecutor(
            max_workers=workers,
            initializer=_initialize_worker,
            initargs=(
                motorData,
                config["variables"],
                config["constraints"],
                mapDim,
            ),
        )
        iterator = executor.map(
            _evaluate_worker,
            items,
            chunksize=max(1, len(items) // (workers * 20)),
        )

    try:
        for completed, row in enumerate(iterator, start=1):
            if row is not None:
                rows.append(row)
            if progress and (
                completed == len(values)
                or completed % max(1, len(values) // 100) == 0
            ):
                progress("Evaluating candidates", completed, len(values))
    finally:
        if executor is not None:
            executor.shutdown()

    if not rows:
        raise RuntimeError("Every candidate simulation failed")
    front = pareto_front(rows, config["objectives"])
    if not front:
        raise RuntimeError("No candidate satisfied all constraints")

    selected = select_cases(front, config["objectives"])
    if progress:
        progress("Validating selected cases", 0, len(selected))
    selected = _validate_selected(
        selected,
        motorData,
        config["variables"],
        config["constraints"],
        int(
            config.get(
                "validation_map_dim",
                motorData["config"].get("mapDim", mapDim or 250),
            )
        ),
    )
    if progress:
        progress(
            "Saving motors and plots", len(selected), len(selected)
        )
    return save_outputs(
        config, motorData, trailer, rows, front, selected
    )


def console_progress(status, current, total):
    percent = 100 * current / total if total else 100
    print(f"\r{status}: {current}/{total} ({percent:5.1f}%)", end="", flush=True)
    if current == total:
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    runParser = subparsers.add_parser("run", help="Run a YAML optimization")
    runParser.add_argument("config", help="Path to optimizer YAML")
    guiParser = subparsers.add_parser("gui", help="Open the optimizer GUI")
    guiParser.add_argument("config", nargs="?", help="Optional optimizer YAML")
    args = parser.parse_args()

    if args.command in (None, "gui"):
        from tools.openmotor_optimizer_gui import launch_gui

        launch_gui(getattr(args, "config", None))
        return

    config = load_config(args.config)
    summary = run_optimization(config, console_progress)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
