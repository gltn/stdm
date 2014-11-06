# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_str_editor.ui'
#
# Created: Fri Jan 03 13:47:53 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_frmSTREditor(object):
    def setupUi(self, frmSTREditor):
        frmSTREditor.setObjectName(_fromUtf8("frmSTREditor"))
        frmSTREditor.resize(352, 132)
        self.gridLayout = QtGui.QGridLayout(frmSTREditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(frmSTREditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.cboSTRType = QtGui.QComboBox(frmSTREditor)
        self.cboSTRType.setMinimumSize(QtCore.QSize(0, 30))
        self.cboSTRType.setObjectName(_fromUtf8("cboSTRType"))
        self.gridLayout.addWidget(self.cboSTRType, 1, 1, 1, 1)
        self.chkSTRAgreement = QtGui.QCheckBox(frmSTREditor)
        self.chkSTRAgreement.setObjectName(_fromUtf8("chkSTRAgreement"))
        self.gridLayout.addWidget(self.chkSTRAgreement, 2, 1, 1, 1)
        self.label_15 = QtGui.QLabel(frmSTREditor)
        self.label_15.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout.addWidget(self.label_15, 1, 0, 1, 1)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)

        self.retranslateUi(frmSTREditor)
        QtCore.QMetaObject.connectSlotsByName(frmSTREditor)

    def retranslateUi(self, frmSTREditor):
        frmSTREditor.setWindowTitle(_translate("frmSTREditor", "Social Tenure Relationship Editor", None))
        self.chkSTRAgreement.setText(_translate("frmSTREditor", "A written agreement is available", None))
        self.label_15.setText(_translate("frmSTREditor", "STR Type", None))

