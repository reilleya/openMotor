from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView
from ..views.SimulationAlertsDialog_ui import Ui_SimAlertsDialog
from motorlib import alertLevelNames, alertTypeNames

class SimulationAlertsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_SimAlertsDialog()
        self.ui.setupUi(self)

        header = self.ui.tableWidgetAlerts.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.hide()

    def displayAlerts(self, simRes):
        self.ui.tableWidgetAlerts.setRowCount(0) # Clear the table
        if len(simRes.alerts) > 0:
            self.ui.tableWidgetAlerts.setRowCount(len(simRes.alerts))
            for row, alert in enumerate(simRes.alerts):
                self.ui.tableWidgetAlerts.setItem(row, 0, QTableWidgetItem(alertLevelNames[alert.level]))
                self.ui.tableWidgetAlerts.setItem(row, 1, QTableWidgetItem(alertTypeNames[alert.type]))
                self.ui.tableWidgetAlerts.setItem(row, 2, QTableWidgetItem(alert.location))
                self.ui.tableWidgetAlerts.setItem(row, 3, QTableWidgetItem(alert.description))
            self.show()
