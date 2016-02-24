# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_varchar_property.ui'
#
# Created: Sun Feb 21 12:26:42 2016
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

class Ui_VarcharProperty(object):
    def setupUi(self, VarcharProperty):
        VarcharProperty.setObjectName(_fromUtf8("VarcharProperty"))
        VarcharProperty.resize(240, 101)
        self.buttonBox = QtGui.QDialogButtonBox(VarcharProperty)
        self.buttonBox.setGeometry(QtCore.QRect(76, 68, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(VarcharProperty)
        self.label.setGeometry(QtCore.QRect(10, 20, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtCharLen = QtGui.QLineEdit(VarcharProperty)
        self.edtCharLen.setGeometry(QtCore.QRect(100, 20, 133, 20))
        self.edtCharLen.setObjectName(_fromUtf8("edtCharLen"))

        self.retranslateUi(VarcharProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), VarcharProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), VarcharProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(VarcharProperty)

    def retranslateUi(self, VarcharProperty):
        VarcharProperty.setWindowTitle(_translate("VarcharProperty", "Varchar property", None))
        self.label.setText(_translate("VarcharProperty", "Character length", None))
        self.edtCharLen.setPlaceholderText(_translate("VarcharProperty", "Enter column length", None))

