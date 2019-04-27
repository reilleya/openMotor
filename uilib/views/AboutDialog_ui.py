# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/AboutDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        AboutDialog.resize(610, 180)
        AboutDialog.setMinimumSize(QtCore.QSize(610, 180))
        AboutDialog.setMaximumSize(QtCore.QSize(610, 180))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("oMIconCycles.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AboutDialog.setWindowIcon(icon)
        AboutDialog.setToolTip("")
        AboutDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelImage = QtWidgets.QLabel(AboutDialog)
        self.labelImage.setText("")
        self.labelImage.setPixmap(QtGui.QPixmap("oMIconCyclesSmall.png"))
        self.labelImage.setObjectName("labelImage")
        self.horizontalLayout_2.addWidget(self.labelImage)
        self.labelText = QtWidgets.QLabel(AboutDialog)
        self.labelText.setObjectName("labelText")
        self.horizontalLayout_2.addWidget(self.labelText)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(AboutDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AboutDialog)
        self.buttonBox.accepted.connect(AboutDialog.accept)
        self.buttonBox.rejected.connect(AboutDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About openMotor"))
        self.labelText.setText(_translate("AboutDialog", "<html><head/><body><p>openMotor ###</p><p>Released under the GNU GPL V3 License.</p><p><a href=\"https://github.com/reilleya/openMotor\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/reilleya/openMotor</span></a></p><p><br/>Warning: Rocket motors can be dangerous! Always verify calculations before testing a motor, <br/>and test far enough away from people and structures to avoid damage. The results from this<br/>program are provided as an estimate and come with no guarantees.</p></body></html>"))


