# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geometry_container.ui'
#
# Created: Wed Jun 20 11:39:25 2018
#      by: PyQt4 UI code generator 4.10.2
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
        GeometryContainer.resize(417, 512)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.help_box = QtGui.QPlainTextEdit(self.groupBox)
        self.help_box.setReadOnly(True)
        self.help_box.setObjectName(_fromUtf8("help_box"))
        self.verticalLayout.addWidget(self.help_box)
        self.gridLayout.addWidget(self.groupBox, 3, 0, 1, 2)
        self.label = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.geom_tools_widgets = QtGui.QStackedWidget(self.dockWidgetContents)
        self.geom_tools_widgets.setObjectName(_fromUtf8("geom_tools_widgets"))
        self.gridLayout.addWidget(self.geom_tools_widgets, 2, 0, 1, 2)
        self.geom_tools_combo = QtGui.QComboBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.geom_tools_combo.sizePolicy().hasHeightForWidth())
        self.geom_tools_combo.setSizePolicy(sizePolicy)
        self.geom_tools_combo.setObjectName(_fromUtf8("geom_tools_combo"))
        self.gridLayout.addWidget(self.geom_tools_combo, 0, 1, 1, 1)
        self.notice_box = QtGui.QVBoxLayout()
        self.notice_box.setObjectName(_fromUtf8("notice_box"))
        self.gridLayout.addLayout(self.notice_box, 1, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        GeometryContainer.setWidget(self.dockWidgetContents)

        self.retranslateUi(GeometryContainer)
        self.geom_tools_widgets.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(GeometryContainer)

    def retranslateUi(self, GeometryContainer):
        GeometryContainer.setWindowTitle(_translate("GeometryContainer", "Geometry Tools", None))
        self.groupBox.setTitle(_translate("GeometryContainer", "Geometry Tools Help", None))
        self.label.setText(_translate("GeometryContainer", "Geometry tools:", None))

