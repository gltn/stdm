# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_value.ui'
#
# Created: Fri Feb 12 10:04:19 2016
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
        LookupValue.resize(400, 145)
        self.gridLayout_2 = QtGui.QGridLayout(LookupValue)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(LookupValue)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtValue = QtGui.QLineEdit(self.groupBox)
        self.edtValue.setObjectName(_fromUtf8("edtValue"))
        self.gridLayout.addWidget(self.edtValue, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.groupBox)
        self.edtCode.setMaximumSize(QtCore.QSize(80, 16777215))
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(LookupValue)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(LookupValue)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupValue.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupValue.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupValue)

    def retranslateUi(self, LookupValue):
        LookupValue.setWindowTitle(_translate("LookupValue", "Dialog", None))
        self.groupBox.setTitle(_translate("LookupValue", "Lookup Value", None))
        self.label.setText(_translate("LookupValue", "Value Name", None))
        self.edtValue.setPlaceholderText(_translate("LookupValue", "Enter lookup value", None))
        self.label_2.setText(_translate("LookupValue", "Code", None))

