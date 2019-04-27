# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/SimulatingDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SimProgressDialog(object):
    def setupUi(self, SimProgressDialog):
        SimProgressDialog.setObjectName("SimProgressDialog")
        SimProgressDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        SimProgressDialog.resize(400, 100)
        SimProgressDialog.setMinimumSize(QtCore.QSize(400, 100))
        SimProgressDialog.setMaximumSize(QtCore.QSize(400, 100))
        SimProgressDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(SimProgressDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SimProgressDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.progressBar = QtWidgets.QProgressBar(SimProgressDialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.buttonBox = QtWidgets.QDialogButtonBox(SimProgressDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SimProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(SimProgressDialog)

    def retranslateUi(self, SimProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        SimProgressDialog.setWindowTitle(_translate("SimProgressDialog", "Simulating"))
        self.label.setText(_translate("SimProgressDialog", "Running simulation..."))


