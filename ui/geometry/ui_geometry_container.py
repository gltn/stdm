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
        GeometryContainer.resize(356, 435)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.geom_tools_combo = QtGui.QComboBox(self.dockWidgetContents)
        self.geom_tools_combo.setObjectName(_fromUtf8("geom_tools_combo"))
        self.gridLayout.addWidget(self.geom_tools_combo, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.geom_tools_widgets = QtGui.QStackedWidget(self.dockWidgetContents)
        self.geom_tools_widgets.setObjectName(_fromUtf8("geom_tools_widgets"))
        self.gridLayout.addWidget(self.geom_tools_widgets, 1, 0, 2, 3)
        GeometryContainer.setWidget(self.dockWidgetContents)

        self.retranslateUi(GeometryContainer)
        self.geom_tools_widgets.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(GeometryContainer)

    def retranslateUi(self, GeometryContainer):
        GeometryContainer.setWindowTitle(_translate("GeometryContainer", "Geometry Tools", None))
        self.label.setText(_translate("GeometryContainer", "Geometry tools:", None))

