# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_value.ui'
#
# Created: Sun Apr 24 14:31:24 2016
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
        LookupValue.resize(249, 95)
        self.formLayout = QtGui.QFormLayout(LookupValue)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(LookupValue)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtValue = QtGui.QLineEdit(LookupValue)
        self.edtValue.setObjectName(_fromUtf8("edtValue"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtValue)
        self.label_2 = QtGui.QLabel(LookupValue)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtCode = QtGui.QLineEdit(LookupValue)
        self.edtCode.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtCode)
        self.buttonBox = QtGui.QDialogButtonBox(LookupValue)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(LookupValue)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupValue.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupValue.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupValue)
        LookupValue.setTabOrder(self.edtValue, self.edtCode)
        LookupValue.setTabOrder(self.edtCode, self.buttonBox)

    def retranslateUi(self, LookupValue):
        LookupValue.setWindowTitle(_translate("LookupValue", "Lookup value", None))
        self.label.setText(_translate("LookupValue", "Value Name", None))
        self.edtValue.setPlaceholderText(_translate("LookupValue", "Enter lookup value", None))
        self.label_2.setText(_translate("LookupValue", "Code", None))

