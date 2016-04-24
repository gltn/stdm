# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_double_property.ui'
#
# Created: Sun Apr 24 14:30:04 2016
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
        self.formLayout = QtGui.QFormLayout(DoubleProperty)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DoubleProperty)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtMinVal = QtGui.QLineEdit(DoubleProperty)
        self.edtMinVal.setObjectName(_fromUtf8("edtMinVal"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtMinVal)
        self.label_2 = QtGui.QLabel(DoubleProperty)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtMaxVal = QtGui.QLineEdit(DoubleProperty)
        self.edtMaxVal.setObjectName(_fromUtf8("edtMaxVal"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtMaxVal)
        self.buttonBox = QtGui.QDialogButtonBox(DoubleProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(DoubleProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DoubleProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DoubleProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(DoubleProperty)

    def retranslateUi(self, DoubleProperty):
        DoubleProperty.setWindowTitle(_translate("DoubleProperty", "Decimal properties", None))
        self.label.setText(_translate("DoubleProperty", "Minimum value", None))
        self.edtMinVal.setPlaceholderText(_translate("DoubleProperty", "Enter minimum value", None))
        self.label_2.setText(_translate("DoubleProperty", "Maximum value", None))
        self.edtMaxVal.setPlaceholderText(_translate("DoubleProperty", "Enter maximum value", None))

