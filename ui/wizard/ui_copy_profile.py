# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_copy_profile.ui'
#
# Created: Tue Mar 07 18:54:01 2017
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

class Ui_dlgCopyProfile(object):
    def setupUi(self, dlgCopyProfile):
        dlgCopyProfile.setObjectName(_fromUtf8("dlgCopyProfile"))
        dlgCopyProfile.resize(445, 128)
        dlgCopyProfile.setMinimumSize(QtCore.QSize(0, 0))
        self.formLayout = QtGui.QFormLayout(dlgCopyProfile)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(dlgCopyProfile)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label)
        self.edtName = QtGui.QLineEdit(dlgCopyProfile)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.edtName)
        self.buttonBox = QtGui.QDialogButtonBox(dlgCopyProfile)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.label_2 = QtGui.QLabel(dlgCopyProfile)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtFromProfile = QtGui.QLineEdit(dlgCopyProfile)
        self.edtFromProfile.setReadOnly(True)
        self.edtFromProfile.setObjectName(_fromUtf8("edtFromProfile"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtFromProfile)
        self.label_3 = QtGui.QLabel(dlgCopyProfile)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.edtDesc = QtGui.QLineEdit(dlgCopyProfile)
        self.edtDesc.setObjectName(_fromUtf8("edtDesc"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.edtDesc)

        self.retranslateUi(dlgCopyProfile)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgCopyProfile.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgCopyProfile.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgCopyProfile)

    def retranslateUi(self, dlgCopyProfile):
        dlgCopyProfile.setWindowTitle(_translate("dlgCopyProfile", "Copy profile", None))
        self.label.setText(_translate("dlgCopyProfile", "To Profile", None))
        self.edtName.setPlaceholderText(_translate("dlgCopyProfile", "Enter profile name", None))
        self.label_2.setText(_translate("dlgCopyProfile", "From Profile", None))
        self.label_3.setText(_translate("dlgCopyProfile", "Description", None))

