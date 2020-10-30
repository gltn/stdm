# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_varchar_property.ui'
#
# Created: Sun Apr 24 14:31:41 2016
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
        VarcharProperty.resize(246, 67)
        self.formLayout = QtGui.QFormLayout(VarcharProperty)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(VarcharProperty)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtCharLen = QtGui.QLineEdit(VarcharProperty)
        self.edtCharLen.setObjectName(_fromUtf8("edtCharLen"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtCharLen)
        self.buttonBox = QtGui.QDialogButtonBox(VarcharProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(VarcharProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), VarcharProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), VarcharProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(VarcharProperty)

    def retranslateUi(self, VarcharProperty):
        VarcharProperty.setWindowTitle(_translate("VarcharProperty", "Varchar property", None))
        self.label.setText(_translate("VarcharProperty", "Character length", None))
        self.edtCharLen.setPlaceholderText(_translate("VarcharProperty", "Enter column length", None))

