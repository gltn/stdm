# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geom_property.ui'
#
# Created: Mon Feb 22 11:16:36 2016
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
        GeometryProperty.resize(261, 108)
        self.buttonBox = QtGui.QDialogButtonBox(GeometryProperty)
        self.buttonBox.setGeometry(QtCore.QRect(90, 80, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(GeometryProperty)
        self.label.setGeometry(QtCore.QRect(10, 8, 72, 16))
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(GeometryProperty)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 90, 16))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.btnCoord = QtGui.QPushButton(GeometryProperty)
        self.btnCoord.setGeometry(QtCore.QRect(110, 40, 141, 23))
        self.btnCoord.setObjectName(_fromUtf8("btnCoord"))
        self.cboGeoType = QtGui.QComboBox(GeometryProperty)
        self.cboGeoType.setGeometry(QtCore.QRect(110, 10, 141, 20))
        self.cboGeoType.setObjectName(_fromUtf8("cboGeoType"))

        self.retranslateUi(GeometryProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), GeometryProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), GeometryProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(GeometryProperty)

    def retranslateUi(self, GeometryProperty):
        GeometryProperty.setWindowTitle(_translate("GeometryProperty", "Geometry properties", None))
        self.label.setText(_translate("GeometryProperty", "Geometry type", None))
        self.label_2.setText(_translate("GeometryProperty", "Coordinate system", None))
        self.btnCoord.setText(_translate("GeometryProperty", "Select ...", None))

