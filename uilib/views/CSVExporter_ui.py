# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/CSVExporter.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CSVExporter(object):
    def setupUi(self, CSVExporter):
        CSVExporter.setObjectName("CSVExporter")
        CSVExporter.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("oMIconCycles.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        CSVExporter.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(CSVExporter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(CSVExporter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.groupBoxChecks = QtWidgets.QGroupBox(CSVExporter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxChecks.sizePolicy().hasHeightForWidth())
        self.groupBoxChecks.setSizePolicy(sizePolicy)
        self.groupBoxChecks.setObjectName("groupBoxChecks")
        self.verticalLayout.addWidget(self.groupBoxChecks)
        self.buttonBox = QtWidgets.QDialogButtonBox(CSVExporter)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CSVExporter)
        self.buttonBox.accepted.connect(CSVExporter.accept)
        self.buttonBox.rejected.connect(CSVExporter.reject)
        QtCore.QMetaObject.connectSlotsByName(CSVExporter)

    def retranslateUi(self, CSVExporter):
        _translate = QtCore.QCoreApplication.translate
        CSVExporter.setWindowTitle(_translate("CSVExporter", "Export CSV"))
        self.label.setText(_translate("CSVExporter", "Simulation must have been run to export a CSV."))
        self.groupBoxChecks.setTitle(_translate("CSVExporter", "Channels"))


