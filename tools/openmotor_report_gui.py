"""PyQt front end for the openMotor engineering report generator."""

import traceback
from pathlib import Path

import yaml
from PyQt6.QtCore import QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from tools.openmotor_report import (
    DEFAULT_TEMPLATE,
    generate_report,
    load_report_config,
    validate_report_config,
)


class ReportThread(QThread):
    progressChanged = pyqtSignal(str, int, int)
    reportReady = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            result = generate_report(
                self.config,
                lambda status, current, total: self.progressChanged.emit(
                    status, current, total
                ),
            )
            self.reportReady.emit(result)
        except Exception:
            self.failed.emit(traceback.format_exc())


class ReportWindow(QMainWindow):
    def __init__(self, configPath=None):
        super().__init__()
        self.setWindowTitle("openMotor Engineering Report Generator")
        self.resize(900, 720)
        self.thread = None
        self.generatedReport = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(self._buildFiles())
        layout.addWidget(self._buildMetadata())
        layout.addWidget(self._buildOptions())
        layout.addLayout(self._buildActions())
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setPlaceholderText(
            "Generated report details will appear here."
        )
        layout.addWidget(self.summary, 1)

        if configPath:
            self.loadConfiguration(configPath)
        else:
            self.templatePath.setText(str(DEFAULT_TEMPLATE.resolve()))

    def _buildFiles(self):
        group = QGroupBox("Files")
        layout = QFormLayout(group)
        self.motorPath = self._pathRow(
            layout,
            "openMotor file",
            "openMotor files (*.ric)",
            save=False,
        )
        self.outputPath = self._pathRow(
            layout,
            "Word report",
            "Word documents (*.docx)",
            save=True,
        )
        self.templatePath = self._pathRow(
            layout,
            "Report template",
            "YAML files (*.yaml *.yml)",
            save=False,
        )
        return group

    def _pathRow(self, layout, label, fileFilter, save):
        field = QLineEdit()
        button = QPushButton("Browse...")

        def browse():
            if save:
                path, _ = QFileDialog.getSaveFileName(
                    self, label, "", fileFilter
                )
            else:
                path, _ = QFileDialog.getOpenFileName(
                    self, label, "", fileFilter
                )
            if path:
                field.setText(path)

        button.clicked.connect(browse)
        row = QHBoxLayout()
        row.addWidget(field)
        row.addWidget(button)
        layout.addRow(label, row)
        return field

    def _buildMetadata(self):
        group = QGroupBox("Document metadata")
        layout = QFormLayout(group)
        self.metadataFields = {}
        defaults = {
            "motor_name": "",
            "project": "openMotor Engineering Analysis",
            "prepared_by": "",
            "organization": "",
            "document_id": "OMR-001",
            "revision": "A",
            "status": "Preliminary",
            "date": "auto",
        }
        labels = {
            "motor_name": "Motor name",
            "project": "Project",
            "prepared_by": "Prepared by",
            "organization": "Organization",
            "document_id": "Document ID",
            "revision": "Revision",
            "status": "Status",
            "date": "Date (YYYY-MM-DD or auto)",
        }
        for key, value in defaults.items():
            field = QLineEdit(value)
            self.metadataFields[key] = field
            layout.addRow(labels[key], field)
        return group

    def _buildOptions(self):
        group = QGroupBox("Simulation and figures")
        layout = QHBoxLayout(group)
        self.mapDim = self._spin(250, 2000, 750)
        self.figureDpi = self._spin(72, 600, 180)
        self.regressionMapDim = self._spin(64, 1000, 300)
        self.regressionContours = self._spin(2, 30, 7)
        for label, widget in (
            ("Map dimension", self.mapDim),
            ("Figure DPI", self.figureDpi),
            ("Regression map", self.regressionMapDim),
            ("Regression contours", self.regressionContours),
        ):
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)
        return group

    @staticmethod
    def _spin(minimum, maximum, value):
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        return spin

    def _buildActions(self):
        layout = QHBoxLayout()
        loadButton = QPushButton("Load configuration")
        saveButton = QPushButton("Save configuration")
        self.generateButton = QPushButton("Generate Word report")
        self.openButton = QPushButton("Open generated report")
        self.openButton.setEnabled(False)
        loadButton.clicked.connect(self.loadConfigurationDialog)
        saveButton.clicked.connect(self.saveConfigurationDialog)
        self.generateButton.clicked.connect(self.generate)
        self.openButton.clicked.connect(self.openReport)
        layout.addWidget(loadButton)
        layout.addWidget(saveButton)
        layout.addWidget(self.generateButton)
        layout.addWidget(self.openButton)
        self.status = QLabel("Ready")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.status, 1)
        layout.addWidget(self.progress)
        return layout

    def configuration(self):
        metadata = {
            key: field.text().strip()
            for key, field in self.metadataFields.items()
        }
        config = {
            "motor": self.motorPath.text().strip(),
            "output": self.outputPath.text().strip(),
            "template": self.templatePath.text().strip(),
            "metadata": metadata,
            "simulation": {"map_dim": self.mapDim.value()},
            "figures": {
                "dpi": self.figureDpi.value(),
                "regression_map_dim": self.regressionMapDim.value(),
                "regression_contours": self.regressionContours.value(),
                "keep_png_files": True,
            },
        }
        validate_report_config(config)
        return config

    def applyConfiguration(self, config):
        self.motorPath.setText(config["motor"])
        self.outputPath.setText(config["output"])
        self.templatePath.setText(config["template"])
        for key, field in self.metadataFields.items():
            field.setText(str(config.get("metadata", {}).get(key, "")))
        self.mapDim.setValue(
            int(config.get("simulation", {}).get("map_dim", 750))
        )
        figures = config.get("figures", {})
        self.figureDpi.setValue(int(figures.get("dpi", 180)))
        self.regressionMapDim.setValue(
            int(figures.get("regression_map_dim", 300))
        )
        self.regressionContours.setValue(
            int(figures.get("regression_contours", 7))
        )

    def loadConfigurationDialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load report configuration",
            "",
            "YAML files (*.yaml *.yml)",
        )
        if path:
            self.loadConfiguration(path)

    def loadConfiguration(self, path):
        try:
            config = load_report_config(path)
            self.applyConfiguration(config)
            self.status.setText(f"Loaded {Path(path).name}")
        except Exception as error:
            QMessageBox.critical(self, "Configuration error", str(error))

    def saveConfigurationDialog(self):
        try:
            config = self.configuration()
        except Exception as error:
            QMessageBox.critical(self, "Configuration error", str(error))
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save report configuration",
            "report.yaml",
            "YAML files (*.yaml *.yml)",
        )
        if path:
            Path(path).write_text(
                yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
            )
            self.status.setText(f"Saved {Path(path).name}")

    def generate(self):
        try:
            config = self.configuration()
        except Exception as error:
            QMessageBox.critical(self, "Configuration error", str(error))
            return
        self.generateButton.setEnabled(False)
        self.openButton.setEnabled(False)
        self.progress.setValue(0)
        self.thread = ReportThread(config)
        self.thread.progressChanged.connect(self.updateProgress)
        self.thread.reportReady.connect(self.reportFinished)
        self.thread.failed.connect(self.reportFailed)
        self.thread.start()

    def updateProgress(self, status, current, total):
        self.status.setText(status)
        self.progress.setValue(round(100 * current / total))

    def reportFinished(self, result):
        self.generateButton.setEnabled(True)
        self.openButton.setEnabled(True)
        self.progress.setValue(100)
        self.status.setText("Report generated")
        self.generatedReport = Path(result["output"])
        self.summary.setPlainText(
            "\n".join(
                [
                    f"Report: {result['output']}",
                    f"Figures: {result['figures'] or 'embedded only'}",
                    f"Designation: {result['designation']}",
                    f"Impulse: {result['impulse_Ns']:.1f} N s",
                    f"Burn time: {result['burn_time_s']:.3f} s",
                    (
                        "Peak pressure: "
                        f"{result['peak_pressure_Pa'] / 1e6:.4f} MPa"
                    ),
                    (
                        "Average pressure: "
                        f"{result['average_pressure_Pa'] / 1e6:.4f} MPa"
                    ),
                    (
                        "Propellant mass: "
                        f"{result['propellant_mass_kg']:.4f} kg"
                    ),
                ]
            )
        )

    def reportFailed(self, details):
        self.generateButton.setEnabled(True)
        self.status.setText("Report generation failed")
        QMessageBox.critical(self, "Report generation failed", details)

    def openReport(self):
        if self.generatedReport:
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(self.generatedReport))
            )


def launch_gui(configPath=None):
    application = QApplication.instance() or QApplication([])
    window = ReportWindow(configPath)
    window.show()
    application.exec()

