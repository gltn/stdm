# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geometry_container.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_GeometryContainer(object):
    def setupUi(self, GeometryContainer):
        GeometryContainer.setObjectName(_fromUtf8("GeometryContainer"))
        GeometryContainer.resize(354, 435)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 2)
        self.stackedWidget = QtGui.QStackedWidget(self.dockWidgetContents)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.page_1 = QtGui.QWidget()
        self.page_1.setObjectName(_fromUtf8("page_1"))
        self.stackedWidget.addWidget(self.page_1)
        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName(_fromUtf8("page_3"))
        self.gridLayout_2 = QtGui.QGridLayout(self.page_3)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.stackedWidget.addWidget(self.page_3)
        self.gridLayout.addWidget(self.stackedWidget, 1, 0, 2, 3)
        GeometryContainer.setWidget(self.dockWidgetContents)

        self.retranslateUi(GeometryContainer)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GeometryContainer)

    def retranslateUi(self, GeometryContainer):
        GeometryContainer.setWindowTitle(_translate("GeometryContainer", "STDM Geometry Tools", None))
        self.label.setText(_translate("GeometryContainer", "Geometry tools:", None))
        self.comboBox.setItemText(0, _translate("GeometryContainer", "Split Polyon: Move line and Area", None))

