# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_entity.ui'
#
# Created: Tue Feb 23 12:34:02 2016
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

class Ui_dlgEntity(object):
    def setupUi(self, dlgEntity):
        dlgEntity.setObjectName(_fromUtf8("dlgEntity"))
        dlgEntity.resize(310, 141)
        self.buttonBox = QtGui.QDialogButtonBox(dlgEntity)
        self.buttonBox.setGeometry(QtCore.QRect(140, 109, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.edtDesc = QtGui.QLineEdit(dlgEntity)
        self.edtDesc.setGeometry(QtCore.QRect(79, 40, 221, 20))
        self.edtDesc.setMinimumSize(QtCore.QSize(120, 0))
        self.edtDesc.setObjectName(_fromUtf8("edtDesc"))
        self.label_2 = QtGui.QLabel(dlgEntity)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 53, 16))
        self.label_2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label = QtGui.QLabel(dlgEntity)
        self.label.setGeometry(QtCore.QRect(14, 10, 60, 16))
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtTable = QtGui.QLineEdit(dlgEntity)
        self.edtTable.setGeometry(QtCore.QRect(80, 10, 221, 20))
        self.edtTable.setObjectName(_fromUtf8("edtTable"))
        self.cbSupportDoc = QtGui.QCheckBox(dlgEntity)
        self.cbSupportDoc.setGeometry(QtCore.QRect(80, 73, 161, 17))
        self.cbSupportDoc.setObjectName(_fromUtf8("cbSupportDoc"))

        self.retranslateUi(dlgEntity)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgEntity.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgEntity.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgEntity)

    def retranslateUi(self, dlgEntity):
        dlgEntity.setWindowTitle(_translate("dlgEntity", "Entity editor", None))
        self.edtDesc.setPlaceholderText(_translate("dlgEntity", "Table description", None))
        self.label_2.setText(_translate("dlgEntity", "Description", None))
        self.label.setText(_translate("dlgEntity", "Entity Name", None))
        self.edtTable.setPlaceholderText(_translate("dlgEntity", "Table name", None))
        self.cbSupportDoc.setText(_translate("dlgEntity", "Allow supporting documents ?", None))

