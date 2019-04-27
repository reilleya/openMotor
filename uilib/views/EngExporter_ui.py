# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/EngExporter.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EngExporterDialog(object):
    def setupUi(self, EngExporterDialog):
        EngExporterDialog.setObjectName("EngExporterDialog")
        EngExporterDialog.resize(400, 400)
        EngExporterDialog.setMinimumSize(QtCore.QSize(400, 400))
        EngExporterDialog.setMaximumSize(QtCore.QSize(400, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("oMIconCycles.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EngExporterDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(EngExporterDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(EngExporterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.motorStats = engExportEditor(EngExporterDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.motorStats.sizePolicy().hasHeightForWidth())
        self.motorStats.setSizePolicy(sizePolicy)
        self.motorStats.setObjectName("motorStats")
        self.verticalLayout.addWidget(self.motorStats)
        self.buttonBox = QtWidgets.QDialogButtonBox(EngExporterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EngExporterDialog)
        self.buttonBox.accepted.connect(EngExporterDialog.accept)
        self.buttonBox.rejected.connect(EngExporterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EngExporterDialog)

    def retranslateUi(self, EngExporterDialog):
        _translate = QtCore.QCoreApplication.translate
        EngExporterDialog.setWindowTitle(_translate("EngExporterDialog", "Export .eng file"))
        self.label.setText(_translate("EngExporterDialog", "Simulation must have been run to export a RASP .eng file."))


from uilib import engExportEditor
