# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_property.ui'
#
# Created: Mon Feb 22 11:13:39 2016
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

class Ui_LookupProperty(object):
    def setupUi(self, LookupProperty):
        LookupProperty.setObjectName(_fromUtf8("LookupProperty"))
        LookupProperty.resize(331, 90)
        self.buttonBox = QtGui.QDialogButtonBox(LookupProperty)
        self.buttonBox.setGeometry(QtCore.QRect(170, 59, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(LookupProperty)
        self.label.setGeometry(QtCore.QRect(10, 20, 41, 16))
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.cboPrimaryEntity = QtGui.QComboBox(LookupProperty)
        self.cboPrimaryEntity.setGeometry(QtCore.QRect(50, 20, 181, 20))
        self.cboPrimaryEntity.setObjectName(_fromUtf8("cboPrimaryEntity"))
        self.edtNewlookup = QtGui.QPushButton(LookupProperty)
        self.edtNewlookup.setGeometry(QtCore.QRect(246, 18, 78, 23))
        self.edtNewlookup.setObjectName(_fromUtf8("edtNewlookup"))

        self.retranslateUi(LookupProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupProperty)

    def retranslateUi(self, LookupProperty):
        LookupProperty.setWindowTitle(_translate("LookupProperty", "Lookup property", None))
        self.label.setText(_translate("LookupProperty", "Lookup", None))
        self.edtNewlookup.setText(_translate("LookupProperty", "New lookup ...", None))

