# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_double_property.ui'
#
# Created: Sun Feb 21 12:27:03 2016
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

class Ui_DoubleProperty(object):
    def setupUi(self, DoubleProperty):
        DoubleProperty.setObjectName(_fromUtf8("DoubleProperty"))
        DoubleProperty.resize(239, 100)
        self.buttonBox = QtGui.QDialogButtonBox(DoubleProperty)
        self.buttonBox.setGeometry(QtCore.QRect(80, 70, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.edtMinVal = QtGui.QLineEdit(DoubleProperty)
        self.edtMinVal.setGeometry(QtCore.QRect(99, 12, 133, 20))
        self.edtMinVal.setObjectName(_fromUtf8("edtMinVal"))
        self.label_2 = QtGui.QLabel(DoubleProperty)
        self.label_2.setGeometry(QtCore.QRect(20, 41, 73, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label = QtGui.QLabel(DoubleProperty)
        self.label.setGeometry(QtCore.QRect(20, 12, 69, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtMaxVal = QtGui.QLineEdit(DoubleProperty)
        self.edtMaxVal.setGeometry(QtCore.QRect(99, 41, 133, 20))
        self.edtMaxVal.setObjectName(_fromUtf8("edtMaxVal"))

        self.retranslateUi(DoubleProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DoubleProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DoubleProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(DoubleProperty)

    def retranslateUi(self, DoubleProperty):
        DoubleProperty.setWindowTitle(_translate("DoubleProperty", "Decimal properties", None))
        self.edtMinVal.setPlaceholderText(_translate("DoubleProperty", "Enter minimum value", None))
        self.label_2.setText(_translate("DoubleProperty", "Maximum value", None))
        self.label.setText(_translate("DoubleProperty", "Minimum value", None))
        self.edtMaxVal.setPlaceholderText(_translate("DoubleProperty", "Enter maximum value", None))

