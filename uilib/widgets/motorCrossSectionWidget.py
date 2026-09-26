"""Interactive longitudinal motor section for simulation results."""

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from motorlib.longitudinal import draw_motor_cross_section


class MotorCrossSectionWidget(FigureCanvas):

    def __init__(self, parent=None):
        self.figure = Figure()
        super().__init__(self.figure)
        self.setParent(parent)
        self.plot = self.figure.add_subplot(111)
        self.figure.tight_layout()

    def showData(self, motor, regressions):
        draw_motor_cross_section(
            self.plot,
            motor,
            regressions=regressions,
            show_labels=True,
        )
        self.figure.tight_layout()
        self.draw()

    def resetPlot(self):
        self.plot.clear()
        self.draw()
