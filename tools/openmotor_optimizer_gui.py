"""PyQt front end for the standalone openMotor optimizer."""

import json
import os
import traceback
from pathlib import Path

import yaml
from PyQt6.QtCore import QThread, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tools.openmotor_optimizer import (
    METRIC_UNITS,
    load_config,
    load_motor,
    numeric_property_paths,
    run_optimization,
    validate_config,
)


class OptimizationThread(QThread):
    progressChanged = pyqtSignal(str, int, int)
    resultReady = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            summary = run_optimization(
                self.config,
                lambda status, current, total: self.progressChanged.emit(
                    status, current, total
                ),
            )
            self.resultReady.emit(summary)
        except Exception:
            self.failed.emit(traceback.format_exc())


class OptimizerWindow(QMainWindow):
    def __init__(self, configPath=None):
        super().__init__()
        self.setWindowTitle("openMotor Optimizer")
        self.resize(1180, 820)
        self.thread = None
        self.lastOutputDirectory = None
        self.variablePathOptions = []

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addWidget(self._buildFilesGroup())
        layout.addWidget(self._buildSettingsGroup())
        layout.addWidget(self._buildConfigurationTabs(), 2)
        layout.addLayout(self._buildActions())
        layout.addWidget(self._buildResultsTabs(), 2)

        if configPath:
            self.loadConfiguration(configPath)

    def _buildFilesGroup(self):
        group = QGroupBox("Files")
        layout = QGridLayout(group)
        self.motorPath = QLineEdit()
        self.motorPath.editingFinished.connect(
            self.refreshVariablePathOptions
        )
        self.outputPath = QLineEdit()
        motorBrowse = QPushButton("Browse...")
        outputBrowse = QPushButton("Browse...")
        motorBrowse.clicked.connect(self.browseMotor)
        outputBrowse.clicked.connect(self.browseOutput)
        layout.addWidget(QLabel("Motor file"), 0, 0)
        layout.addWidget(self.motorPath, 0, 1)
        layout.addWidget(motorBrowse, 0, 2)
        layout.addWidget(QLabel("Output directory"), 1, 0)
        layout.addWidget(self.outputPath, 1, 1)
        layout.addWidget(outputBrowse, 1, 2)
        return group

    def _buildSettingsGroup(self):
        group = QGroupBox("Search settings")
        layout = QFormLayout(group)
        row = QHBoxLayout()
        self.samples = self._integerBox(1, 10_000_000, 2000)
        self.workers = self._integerBox(
            1, 128, max(1, (os.cpu_count() or 2) - 1)
        )
        self.seed = self._integerBox(0, 2_147_483_647, 1)
        self.mapDim = self._integerBox(0, 10000, 250)
        self.validationMapDim = self._integerBox(0, 10000, 750)
        for label, widget in (
            ("Samples", self.samples),
            ("Workers", self.workers),
            ("Seed", self.seed),
            ("Search map dimension", self.mapDim),
            ("Validation map dimension", self.validationMapDim),
        ):
            row.addWidget(QLabel(label))
            row.addWidget(widget)
        layout.addRow(row)
        return group

    @staticmethod
    def _integerBox(minimum, maximum, value):
        box = QSpinBox()
        box.setRange(minimum, maximum)
        box.setValue(value)
        return box

    def _buildConfigurationTabs(self):
        tabs = QTabWidget()
        self.variables = self._table(
            ["Name", "Property path(s)", "Minimum", "Maximum", "Type"]
        )
        self.constraints = self._table(["Metric", "Minimum", "Maximum"])
        self.objectives = self._table(["Metric", "Direction"])
        tabs.addTab(
            self._tablePanel(
                self.variables,
                lambda: self.addVariable(),
                lambda: self.removeRow(self.variables),
            ),
            "Variables",
        )
        tabs.addTab(
            self._tablePanel(
                self.constraints,
                lambda: self.addConstraint(),
                lambda: self.removeRow(self.constraints),
            ),
            "Constraints",
        )
        tabs.addTab(
            self._tablePanel(
                self.objectives,
                lambda: self.addObjective(),
                lambda: self.removeRow(self.objectives),
            ),
            "Objectives",
        )
        return tabs

    @staticmethod
    def _table(headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        return table

    @staticmethod
    def _tablePanel(table, addCallback, removeCallback):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(table)
        buttons = QHBoxLayout()
        add = QPushButton("Add")
        remove = QPushButton("Remove selected")
        add.clicked.connect(addCallback)
        remove.clicked.connect(removeCallback)
        buttons.addWidget(add)
        buttons.addWidget(remove)
        buttons.addStretch()
        layout.addLayout(buttons)
        return panel

    def _buildActions(self):
        layout = QHBoxLayout()
        load = QPushButton("Load configuration")
        save = QPushButton("Save configuration")
        self.runButton = QPushButton("Run optimization")
        self.openOutputButton = QPushButton("Open output directory")
        self.openOutputButton.setEnabled(False)
        load.clicked.connect(self.loadConfigurationDialog)
        save.clicked.connect(self.saveConfigurationDialog)
        self.runButton.clicked.connect(self.runOptimization)
        self.openOutputButton.clicked.connect(self.openOutput)
        layout.addWidget(load)
        layout.addWidget(save)
        layout.addWidget(self.runButton)
        layout.addWidget(self.openOutputButton)
        self.statusLabel = QLabel("Ready")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.statusLabel, 1)
        layout.addWidget(self.progress)
        return layout

    def _buildResultsTabs(self):
        tabs = QTabWidget()
        self.results = self._table([])
        self.paretoImage = self._imageLabel()
        self.pressureImage = self._imageLabel()
        tabs.addTab(self.results, "Selected cases")
        tabs.addTab(self.paretoImage, "Pareto plot")
        tabs.addTab(self.pressureImage, "Pressure plot")
        return tabs

    @staticmethod
    def _imageLabel():
        label = QLabel("Run an optimization to generate this plot.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumHeight(250)
        return label

    def addVariable(self, variable=None):
        variable = variable or {
            "name": "variable",
            "paths": ["grains[0].properties.length"],
            "min": 0.01,
            "max": 0.10,
            "type": "float",
        }
        row = self.variables.rowCount()
        self.variables.insertRow(row)
        values = (
            variable["name"],
            variable["min"],
            variable["max"],
        )
        for column, value in zip((0, 2, 3), values):
            self.variables.setItem(
                row, column, QTableWidgetItem(str(value))
            )
        pathCombo = self._propertyPathCombo(
            "; ".join(variable["paths"])
        )
        self.variables.setCellWidget(row, 1, pathCombo)
        combo = QComboBox()
        combo.addItems(["float", "integer"])
        combo.setCurrentText(variable.get("type", "float"))
        self.variables.setCellWidget(row, 4, combo)

    def addConstraint(self, constraint=None):
        constraint = constraint or {
            "metric": "impulse",
            "min": 0,
        }
        row = self.constraints.rowCount()
        self.constraints.insertRow(row)
        self.constraints.setCellWidget(
            row, 0, self._metricCombo(constraint["metric"])
        )
        for column, field in ((1, "min"), (2, "max")):
            value = constraint.get(field, "")
            self.constraints.setItem(
                row, column, QTableWidgetItem(str(value))
            )

    def addObjective(self, objective=None):
        objective = objective or {
            "metric": "propellant_mass",
            "direction": "minimize",
        }
        row = self.objectives.rowCount()
        self.objectives.insertRow(row)
        self.objectives.setCellWidget(
            row, 0, self._metricCombo(objective["metric"])
        )
        direction = QComboBox()
        direction.addItems(["minimize", "maximize"])
        direction.setCurrentText(objective.get("direction", "minimize"))
        self.objectives.setCellWidget(row, 1, direction)

    @staticmethod
    def _metricCombo(value):
        combo = QComboBox()
        combo.addItems(METRIC_UNITS)
        combo.setCurrentText(value)
        return combo

    def _propertyPathCombo(self, value=""):
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.addItems(self.variablePathOptions)
        combo.setCurrentText(value)
        combo.setToolTip(
            "Select one numeric motor property, or enter multiple paths "
            "separated by semicolons to link them."
        )
        return combo

    def refreshVariablePathOptions(self):
        motorPath = self.motorPath.text().strip()
        try:
            motorData, _ = load_motor(motorPath)
            self.variablePathOptions = numeric_property_paths(motorData)
        except (OSError, TypeError, ValueError, yaml.YAMLError):
            self.variablePathOptions = []

        for row in range(self.variables.rowCount()):
            combo = self.variables.cellWidget(row, 1)
            if combo is None:
                continue
            current = combo.currentText()
            combo.clear()
            combo.addItems(self.variablePathOptions)
            combo.setCurrentText(current)

    @staticmethod
    def removeRow(table):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    def browseMotor(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select motor", "", "openMotor files (*.ric)"
        )
        if path:
            self.motorPath.setText(path)
            self.refreshVariablePathOptions()

    def browseOutput(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select output directory"
        )
        if path:
            self.outputPath.setText(path)

    def loadConfigurationDialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load optimizer configuration", "", "YAML files (*.yaml *.yml)"
        )
        if path:
            self.loadConfiguration(path)

    def loadConfiguration(self, path):
        try:
            config = load_config(path)
            self.applyConfiguration(config)
            self.statusLabel.setText(f"Loaded {Path(path).name}")
        except Exception as error:
            QMessageBox.critical(self, "Configuration error", str(error))

    def applyConfiguration(self, config):
        self.motorPath.setText(config["motor"])
        self.refreshVariablePathOptions()
        self.outputPath.setText(config["output_directory"])
        self.samples.setValue(int(config.get("samples", 2000)))
        self.workers.setValue(int(config.get("workers", 1)))
        self.seed.setValue(int(config.get("seed", 1)))
        self.mapDim.setValue(int(config.get("map_dim", 0) or 0))
        self.validationMapDim.setValue(
            int(config.get("validation_map_dim", 0) or 0)
        )
        self.variables.setRowCount(0)
        self.constraints.setRowCount(0)
        self.objectives.setRowCount(0)
        for variable in config["variables"]:
            self.addVariable(variable)
        for constraint in config["constraints"]:
            self.addConstraint(constraint)
        for objective in config["objectives"]:
            self.addObjective(objective)

    def saveConfigurationDialog(self):
        try:
            config = self.configuration()
        except Exception as error:
            QMessageBox.critical(self, "Configuration error", str(error))
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save optimizer configuration",
            "optimizer.yaml",
            "YAML files (*.yaml *.yml)",
        )
        if path:
            Path(path).write_text(
                yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
            )
            self.statusLabel.setText(f"Saved {Path(path).name}")

    def configuration(self):
        variables = []
        for row in range(self.variables.rowCount()):
            paths = [
                path.strip()
                for path in self.variables.cellWidget(
                    row, 1
                ).currentText().split(";")
                if path.strip()
            ]
            variables.append(
                {
                    "name": self._cell(self.variables, row, 0),
                    "paths": paths,
                    "min": float(self._cell(self.variables, row, 2)),
                    "max": float(self._cell(self.variables, row, 3)),
                    "type": self.variables.cellWidget(row, 4).currentText(),
                }
            )

        constraints = []
        for row in range(self.constraints.rowCount()):
            constraint = {
                "metric": self.constraints.cellWidget(row, 0).currentText()
            }
            for column, field in ((1, "min"), (2, "max")):
                value = self._cell(self.constraints, row, column).strip()
                if value:
                    constraint[field] = float(value)
            constraints.append(constraint)

        objectives = []
        for row in range(self.objectives.rowCount()):
            objectives.append(
                {
                    "metric": self.objectives.cellWidget(
                        row, 0
                    ).currentText(),
                    "direction": self.objectives.cellWidget(
                        row, 1
                    ).currentText(),
                }
            )

        config = {
            "motor": self.motorPath.text().strip(),
            "output_directory": self.outputPath.text().strip(),
            "samples": self.samples.value(),
            "workers": self.workers.value(),
            "seed": self.seed.value(),
            "include_current": True,
            "variables": variables,
            "constraints": constraints,
            "objectives": objectives,
        }
        if self.mapDim.value():
            config["map_dim"] = self.mapDim.value()
        if self.validationMapDim.value():
            config["validation_map_dim"] = self.validationMapDim.value()
        validate_config(config)
        return config

    @staticmethod
    def _cell(table, row, column):
        item = table.item(row, column)
        return item.text() if item else ""

    def runOptimization(self):
        try:
            config = self.configuration()
        except Exception as error:
            QMessageBox.critical(self, "Configuration error", str(error))
            return

        self.runButton.setEnabled(False)
        self.openOutputButton.setEnabled(False)
        self.progress.setValue(0)
        self.statusLabel.setText("Starting...")
        self.thread = OptimizationThread(config)
        self.thread.progressChanged.connect(self.updateProgress)
        self.thread.resultReady.connect(
            lambda summary: self.optimizationFinished(config, summary)
        )
        self.thread.failed.connect(self.optimizationFailed)
        self.thread.start()

    def updateProgress(self, status, current, total):
        self.statusLabel.setText(status)
        self.progress.setValue(
            round(100 * current / total) if total else 100
        )

    def optimizationFinished(self, config, summary):
        self.runButton.setEnabled(True)
        self.openOutputButton.setEnabled(True)
        self.progress.setValue(100)
        self.statusLabel.setText(
            f"Finished: {summary['feasible_candidates']} feasible, "
            f"{summary['pareto_candidates']} Pareto"
        )
        self.lastOutputDirectory = Path(config["output_directory"])
        self.showResults(summary)
        self.showImage(
            self.paretoImage,
            self.lastOutputDirectory / "pareto-front.png",
        )
        self.showImage(
            self.pressureImage,
            self.lastOutputDirectory / "pressure-comparison.png",
        )

    def optimizationFailed(self, details):
        self.runButton.setEnabled(True)
        self.statusLabel.setText("Optimization failed")
        QMessageBox.critical(self, "Optimization failed", details)

    def showResults(self, summary):
        selected = summary["selected"]
        if not selected:
            return
        fields = [
            field
            for field in next(iter(selected.values()))
            if field not in ("candidate", "feasible")
        ]
        self.results.setColumnCount(len(fields) + 1)
        self.results.setHorizontalHeaderLabels(["Case"] + fields)
        self.results.setRowCount(len(selected))
        for row, (label, values) in enumerate(selected.items()):
            self.results.setItem(
                row, 0, QTableWidgetItem(label.replace("_", " ").title())
            )
            for column, field in enumerate(fields, start=1):
                value = values[field]
                text = f"{value:.8g}" if isinstance(value, float) else str(value)
                self.results.setItem(row, column, QTableWidgetItem(text))
        self.results.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

    @staticmethod
    def showImage(label, path):
        if not path.exists():
            label.setText("No plot was generated.")
            return
        pixmap = QPixmap(str(path))
        label.setPixmap(
            pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def openOutput(self):
        if self.lastOutputDirectory:
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(self.lastOutputDirectory))
            )


def launch_gui(configPath=None):
    application = QApplication.instance() or QApplication([])
    window = OptimizerWindow(configPath)
    window.show()
    application.exec()
