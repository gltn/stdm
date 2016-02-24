# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_bigint_property.ui'
#
# Created: Sun Feb 21 12:26:38 2016
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

class Ui_BigintProperty(object):
    def setupUi(self, BigintProperty):
        BigintProperty.setObjectName(_fromUtf8("BigintProperty"))
        BigintProperty.resize(244, 101)
        self.buttonBox = QtGui.QDialogButtonBox(BigintProperty)
        self.buttonBox.setGeometry(QtCore.QRect(74, 74, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.edtMinVal = QtGui.QLineEdit(BigintProperty)
        self.edtMinVal.setGeometry(QtCore.QRect(100, 12, 133, 20))
        self.edtMinVal.setObjectName(_fromUtf8("edtMinVal"))
        self.edtMaxVal = QtGui.QLineEdit(BigintProperty)
        self.edtMaxVal.setGeometry(QtCore.QRect(100, 42, 133, 20))
        self.edtMaxVal.setObjectName(_fromUtf8("edtMaxVal"))
        self.label_2 = QtGui.QLabel(BigintProperty)
        self.label_2.setGeometry(QtCore.QRect(21, 42, 73, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label = QtGui.QLabel(BigintProperty)
        self.label.setGeometry(QtCore.QRect(21, 12, 69, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(BigintProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BigintProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BigintProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(BigintProperty)

    def retranslateUi(self, BigintProperty):
        BigintProperty.setWindowTitle(_translate("BigintProperty", "Bigint properties", None))
        self.edtMinVal.setPlaceholderText(_translate("BigintProperty", "Enter minimum value", None))
        self.edtMaxVal.setPlaceholderText(_translate("BigintProperty", "Enter maximum value", None))
        self.label_2.setText(_translate("BigintProperty", "Maximum value", None))
        self.label.setText(_translate("BigintProperty", "Minimum value", None))

