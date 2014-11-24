# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_changepwd.ui'
#
# Created: Tue Nov 18 17:48:29 2014
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_frmChangePwd(object):
    def setupUi(self, frmChangePwd):
        frmChangePwd.setObjectName(_fromUtf8("frmChangePwd"))
        frmChangePwd.resize(320, 200)
        frmChangePwd.setMaximumSize(QtCore.QSize(320, 16777215))
        self.gridLayout_2 = QtGui.QGridLayout(frmChangePwd)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(frmChangePwd)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtNewPass = QtGui.QLineEdit(self.groupBox)
        self.txtNewPass.setMinimumSize(QtCore.QSize(0, 30))
        self.txtNewPass.setMaxLength(200)
        self.txtNewPass.setEchoMode(QtGui.QLineEdit.Password)
        self.txtNewPass.setObjectName(_fromUtf8("txtNewPass"))
        self.gridLayout.addWidget(self.txtNewPass, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(70, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtConfirmPass = QtGui.QLineEdit(self.groupBox)
        self.txtConfirmPass.setMinimumSize(QtCore.QSize(0, 30))
        self.txtConfirmPass.setMaxLength(200)
        self.txtConfirmPass.setEchoMode(QtGui.QLineEdit.Password)
        self.txtConfirmPass.setObjectName(_fromUtf8("txtConfirmPass"))
        self.gridLayout.addWidget(self.txtConfirmPass, 1, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.btnBox = QtGui.QDialogButtonBox(frmChangePwd)
        self.btnBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.btnBox.setObjectName(_fromUtf8("btnBox"))
        self.gridLayout_2.addWidget(self.btnBox, 1, 0, 1, 1)

        self.retranslateUi(frmChangePwd)
        QtCore.QObject.connect(self.btnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmChangePwd.reject)
        QtCore.QMetaObject.connectSlotsByName(frmChangePwd)

    def retranslateUi(self, frmChangePwd):
        frmChangePwd.setWindowTitle(_translate("frmChangePwd", "Change Password", None))
        self.groupBox.setTitle(_translate("frmChangePwd", "Change password for the current user", None))
        self.label.setText(_translate("frmChangePwd", "New Password", None))
        self.label_2.setText(_translate("frmChangePwd", "Confirm Password", None))

