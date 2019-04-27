# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/Preferences.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(PreferencesDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tabGeneral = QtWidgets.QWidget()
        self.tabGeneral.setObjectName("tabGeneral")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tabGeneral)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.settingsEditorGeneral = settingsEditor(self.tabGeneral)
        self.settingsEditorGeneral.setObjectName("settingsEditorGeneral")
        self.verticalLayout_2.addWidget(self.settingsEditorGeneral)
        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabUnits = QtWidgets.QWidget()
        self.tabUnits.setObjectName("tabUnits")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tabUnits)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.settingsEditorUnits = settingsEditor(self.tabUnits)
        self.settingsEditorUnits.setObjectName("settingsEditorUnits")
        self.verticalLayout_3.addWidget(self.settingsEditorUnits)
        self.tabWidget.addTab(self.tabUnits, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PreferencesDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        _translate = QtCore.QCoreApplication.translate
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneral), _translate("PreferencesDialog", "General"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabUnits), _translate("PreferencesDialog", "Units"))


from uilib import settingsEditor
