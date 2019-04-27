# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/PropMenu.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PropellantDialog(object):
    def setupUi(self, PropellantDialog):
        PropellantDialog.setObjectName("PropellantDialog")
        PropellantDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PropellantDialog.resize(600, 500)
        PropellantDialog.setMinimumSize(QtCore.QSize(600, 500))
        PropellantDialog.setMaximumSize(QtCore.QSize(600, 500))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("oMIconCycles.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        PropellantDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(PropellantDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 12, 0, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.listWidgetPropellants = QtWidgets.QListWidget(PropellantDialog)
        self.listWidgetPropellants.setMaximumSize(QtCore.QSize(150, 16777215))
        self.listWidgetPropellants.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.listWidgetPropellants.setSelectionRectVisible(True)
        self.listWidgetPropellants.setObjectName("listWidgetPropellants")
        self.verticalLayout_2.addWidget(self.listWidgetPropellants)
        self.pushButtonNewPropellant = QtWidgets.QPushButton(PropellantDialog)
        self.pushButtonNewPropellant.setObjectName("pushButtonNewPropellant")
        self.verticalLayout_2.addWidget(self.pushButtonNewPropellant)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButtonEdit = QtWidgets.QPushButton(PropellantDialog)
        self.pushButtonEdit.setObjectName("pushButtonEdit")
        self.horizontalLayout_2.addWidget(self.pushButtonEdit)
        self.pushButtonDelete = QtWidgets.QPushButton(PropellantDialog)
        self.pushButtonDelete.setObjectName("pushButtonDelete")
        self.horizontalLayout_2.addWidget(self.pushButtonDelete)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.line = QtWidgets.QFrame(PropellantDialog)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.propEditor = propellantEditor(PropellantDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.propEditor.sizePolicy().hasHeightForWidth())
        self.propEditor.setSizePolicy(sizePolicy)
        self.propEditor.setObjectName("propEditor")
        self.horizontalLayout.addWidget(self.propEditor)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(PropellantDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PropellantDialog)
        self.buttonBox.rejected.connect(PropellantDialog.close)
        QtCore.QMetaObject.connectSlotsByName(PropellantDialog)

    def retranslateUi(self, PropellantDialog):
        _translate = QtCore.QCoreApplication.translate
        PropellantDialog.setWindowTitle(_translate("PropellantDialog", "Propellant Editor"))
        self.pushButtonNewPropellant.setText(_translate("PropellantDialog", "New"))
        self.pushButtonEdit.setText(_translate("PropellantDialog", "Edit"))
        self.pushButtonDelete.setText(_translate("PropellantDialog", "Delete"))


from uilib import propellantEditor
