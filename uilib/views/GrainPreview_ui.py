# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tuxxi/Documents/openMotor/uilib/views/forms/GrainPreview.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GrainPreview(object):
    def setupUi(self, GrainPreview):
        GrainPreview.setObjectName("GrainPreview")
        GrainPreview.resize(300, 175)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GrainPreview.sizePolicy().hasHeightForWidth())
        GrainPreview.setSizePolicy(sizePolicy)
        GrainPreview.setMinimumSize(QtCore.QSize(300, 175))
        GrainPreview.setMaximumSize(QtCore.QSize(300, 175))
        self.verticalLayout = QtWidgets.QVBoxLayout(GrainPreview)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(GrainPreview)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabWidget.setObjectName("tabWidget")
        self.tabFace = grainPreviewGraph()
        self.tabFace.setObjectName("tabFace")
        self.tabWidget.addTab(self.tabFace, "")
        self.tabRegression = grainPreviewGraph()
        self.tabRegression.setObjectName("tabRegression")
        self.tabWidget.addTab(self.tabRegression, "")
        self.tabAreaGraph = grainPreviewGraph()
        self.tabAreaGraph.setObjectName("tabAreaGraph")
        self.tabWidget.addTab(self.tabAreaGraph, "")
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(GrainPreview)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GrainPreview)

    def retranslateUi(self, GrainPreview):
        _translate = QtCore.QCoreApplication.translate
        GrainPreview.setWindowTitle(_translate("GrainPreview", "Form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFace), _translate("GrainPreview", "Face"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabRegression), _translate("GrainPreview", "Regression"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAreaGraph), _translate("GrainPreview", "Area Graph"))


from uilib import grainPreviewGraph
