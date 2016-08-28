# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geom_property.ui'
#
# Created: Sat May 28 15:59:30 2016
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_GeometryProperty(object):
    def setupUi(self, GeometryProperty):
        GeometryProperty.setObjectName(_fromUtf8("GeometryProperty"))
        GeometryProperty.resize(290, 108)
        self.gridLayout_2 = QtGui.QGridLayout(GeometryProperty)
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(GeometryProperty)
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cboGeoType = QtGui.QComboBox(GeometryProperty)
        self.cboGeoType.setMaximumSize(QtCore.QSize(500, 16777215))
        self.cboGeoType.setObjectName(_fromUtf8("cboGeoType"))
        self.gridLayout.addWidget(self.cboGeoType, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(GeometryProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.btnCoord = QtGui.QPushButton(GeometryProperty)
        self.btnCoord.setObjectName(_fromUtf8("btnCoord"))
        self.gridLayout.addWidget(self.btnCoord, 1, 1, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(GeometryProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(GeometryProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), GeometryProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), GeometryProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(GeometryProperty)

    def retranslateUi(self, GeometryProperty):
        GeometryProperty.setWindowTitle(_translate("GeometryProperty", "Geometry properties", None))
        self.label.setText(_translate("GeometryProperty", "Geometry type", None))
        self.label_2.setText(_translate("GeometryProperty", "Coordinate system", None))
        self.btnCoord.setText(_translate("GeometryProperty", "Select ...", None))

