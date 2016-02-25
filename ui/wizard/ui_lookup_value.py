# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_value.ui'
#
# Created: Thu Feb 25 11:26:34 2016
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

class Ui_LookupValue(object):
    def setupUi(self, LookupValue):
        LookupValue.setObjectName(_fromUtf8("LookupValue"))
        LookupValue.resize(223, 117)
        self.buttonBox = QtGui.QDialogButtonBox(LookupValue)
        self.buttonBox.setGeometry(QtCore.QRect(55, 88, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(LookupValue)
        self.label.setGeometry(QtCore.QRect(24, 20, 60, 16))
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtCode = QtGui.QLineEdit(LookupValue)
        self.edtCode.setGeometry(QtCore.QRect(83, 52, 131, 20))
        self.edtCode.setMaximumSize(QtCore.QSize(200, 16777215))
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.label_2 = QtGui.QLabel(LookupValue)
        self.label_2.setGeometry(QtCore.QRect(24, 52, 25, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.edtValue = QtGui.QLineEdit(LookupValue)
        self.edtValue.setGeometry(QtCore.QRect(83, 20, 130, 20))
        self.edtValue.setObjectName(_fromUtf8("edtValue"))

        self.retranslateUi(LookupValue)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupValue.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupValue.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupValue)
        LookupValue.setTabOrder(self.edtValue, self.edtCode)
        LookupValue.setTabOrder(self.edtCode, self.buttonBox)

    def retranslateUi(self, LookupValue):
        LookupValue.setWindowTitle(_translate("LookupValue", "Lookup value", None))
        self.label.setText(_translate("LookupValue", "Value Name", None))
        self.label_2.setText(_translate("LookupValue", "Code", None))
        self.edtValue.setPlaceholderText(_translate("LookupValue", "Enter lookup value", None))

