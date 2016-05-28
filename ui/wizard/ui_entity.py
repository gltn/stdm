# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_entity.ui'
#
# Created: Sat May 28 12:27:02 2016
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
        dlgEntity.resize(308, 129)
        dlgEntity.setMaximumSize(QtCore.QSize(500, 16777215))
        self.formLayout = QtGui.QFormLayout(dlgEntity)
        self.formLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(dlgEntity)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtTable = QtGui.QLineEdit(dlgEntity)
        self.edtTable.setObjectName(_fromUtf8("edtTable"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtTable)
        self.label_2 = QtGui.QLabel(dlgEntity)
        self.label_2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtDesc = QtGui.QLineEdit(dlgEntity)
        self.edtDesc.setMinimumSize(QtCore.QSize(120, 0))
        self.edtDesc.setObjectName(_fromUtf8("edtDesc"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtDesc)
        self.cbSupportDoc = QtGui.QCheckBox(dlgEntity)
        self.cbSupportDoc.setObjectName(_fromUtf8("cbSupportDoc"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cbSupportDoc)
        self.buttonBox = QtGui.QDialogButtonBox(dlgEntity)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(dlgEntity)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgEntity.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgEntity.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgEntity)

    def retranslateUi(self, dlgEntity):
        dlgEntity.setWindowTitle(_translate("dlgEntity", "Entity editor", None))
        self.label.setText(_translate("dlgEntity", "Entity Name", None))
        self.edtTable.setPlaceholderText(_translate("dlgEntity", "Table name", None))
        self.label_2.setText(_translate("dlgEntity", "Description", None))
        self.edtDesc.setPlaceholderText(_translate("dlgEntity", "Table description", None))
        self.cbSupportDoc.setText(_translate("dlgEntity", "Allow supporting documents?", None))

