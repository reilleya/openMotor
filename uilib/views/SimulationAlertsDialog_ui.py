# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/SimulationAlertsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SimAlertsDialog(object):
    def setupUi(self, SimAlertsDialog):
        SimAlertsDialog.setObjectName("SimAlertsDialog")
        SimAlertsDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        SimAlertsDialog.resize(700, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SimAlertsDialog.sizePolicy().hasHeightForWidth())
        SimAlertsDialog.setSizePolicy(sizePolicy)
        SimAlertsDialog.setMinimumSize(QtCore.QSize(700, 300))
        SimAlertsDialog.setMaximumSize(QtCore.QSize(700, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("oMIconCycles.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SimAlertsDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(SimAlertsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SimAlertsDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tableWidgetAlerts = QtWidgets.QTableWidget(SimAlertsDialog)
        self.tableWidgetAlerts.setColumnCount(4)
        self.tableWidgetAlerts.setObjectName("tableWidgetAlerts")
        self.tableWidgetAlerts.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetAlerts.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetAlerts.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetAlerts.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetAlerts.setHorizontalHeaderItem(3, item)
        self.verticalLayout.addWidget(self.tableWidgetAlerts)
        self.buttonBox = QtWidgets.QDialogButtonBox(SimAlertsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SimAlertsDialog)
        self.buttonBox.accepted.connect(SimAlertsDialog.accept)
        self.buttonBox.rejected.connect(SimAlertsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SimAlertsDialog)

    def retranslateUi(self, SimAlertsDialog):
        _translate = QtCore.QCoreApplication.translate
        SimAlertsDialog.setWindowTitle(_translate("SimAlertsDialog", "Simulation Output"))
        self.label.setText(_translate("SimAlertsDialog", "All errors must be resolved to view simulation results."))
        item = self.tableWidgetAlerts.horizontalHeaderItem(0)
        item.setText(_translate("SimAlertsDialog", "Level"))
        item = self.tableWidgetAlerts.horizontalHeaderItem(1)
        item.setText(_translate("SimAlertsDialog", "Type"))
        item = self.tableWidgetAlerts.horizontalHeaderItem(2)
        item.setText(_translate("SimAlertsDialog", "Location"))
        item = self.tableWidgetAlerts.horizontalHeaderItem(3)
        item.setText(_translate("SimAlertsDialog", "Details"))


