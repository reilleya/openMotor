import matplotlib

from .preferencesManager import PreferencesManager
from .propellantManager import PropellantManager
from .simulationManager import SimulationManager
from .fileManager import FileManager
from .toolManager import ToolManager
from .importExportManager import ImportExportManager

__all__ = [
    "PreferencesManager",
    "PropellantManager",
    "SimulationManager",
    "FileManager",
    "ToolManager",
    "ImportExportManager",
]

matplotlib.use("Qt5Agg")
