# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_entity.ui'
#
# Created: Thu Mar 03 06:27:36 2016
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

class Ui_dlgLookup(object):
    def setupUi(self, dlgLookup):
        dlgLookup.setObjectName(_fromUtf8("dlgLookup"))
        dlgLookup.resize(291, 100)
        self.buttonBox = QtGui.QDialogButtonBox(dlgLookup)
        self.buttonBox.setGeometry(QtCore.QRect(123, 69, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(dlgLookup)
        self.label.setGeometry(QtCore.QRect(10, 36, 64, 16))
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtName = QtGui.QLineEdit(dlgLookup)
        self.edtName.setGeometry(QtCore.QRect(80, 36, 201, 20))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.label_2 = QtGui.QLabel(dlgLookup)
        self.label_2.setGeometry(QtCore.QRect(10, 4, 291, 16))
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(dlgLookup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgLookup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgLookup.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgLookup)

    def retranslateUi(self, dlgLookup):
        dlgLookup.setWindowTitle(_translate("dlgLookup", "Lookup entity", None))
        self.label.setText(_translate("dlgLookup", "Lookup Name", None))
        self.edtName.setPlaceholderText(_translate("dlgLookup", "Enter lookup name", None))
        self.label_2.setText(_translate("dlgLookup", "Please note \'check\' will be appended to the name entered", None))

