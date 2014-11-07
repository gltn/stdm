# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_changepwd.ui'
#
# Created: Sat Jun 01 20:08:26 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmChangePwd(object):
    def setupUi(self, frmChangePwd):
        frmChangePwd.setObjectName(_fromUtf8("frmChangePwd"))
        frmChangePwd.resize(320, 177)
        frmChangePwd.setMaximumSize(QtCore.QSize(320, 16777215))
        self.gridLayout_2 = QtGui.QGridLayout(frmChangePwd)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtNewPass = QtGui.QLineEdit(frmChangePwd)
        self.txtNewPass.setMinimumSize(QtCore.QSize(0, 30))
        self.txtNewPass.setMaxLength(200)
        self.txtNewPass.setEchoMode(QtGui.QLineEdit.Password)
        self.txtNewPass.setObjectName(_fromUtf8("txtNewPass"))
        self.gridLayout.addWidget(self.txtNewPass, 0, 1, 1, 1)
        self.label = QtGui.QLabel(frmChangePwd)
        self.label.setMinimumSize(QtCore.QSize(70, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(frmChangePwd)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtConfirmPass = QtGui.QLineEdit(frmChangePwd)
        self.txtConfirmPass.setMinimumSize(QtCore.QSize(0, 30))
        self.txtConfirmPass.setMaxLength(200)
        self.txtConfirmPass.setEchoMode(QtGui.QLineEdit.Password)
        self.txtConfirmPass.setObjectName(_fromUtf8("txtConfirmPass"))
        self.gridLayout.addWidget(self.txtConfirmPass, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.btnBox = QtGui.QDialogButtonBox(frmChangePwd)
        self.btnBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.btnBox.setObjectName(_fromUtf8("btnBox"))
        self.gridLayout_2.addWidget(self.btnBox, 1, 0, 1, 1)

        self.retranslateUi(frmChangePwd)
        QtCore.QObject.connect(self.btnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmChangePwd.reject)
        QtCore.QMetaObject.connectSlotsByName(frmChangePwd)

    def retranslateUi(self, frmChangePwd):
        frmChangePwd.setWindowTitle(QtGui.QApplication.translate("frmChangePwd", "Change Password", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmChangePwd", "New Password", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmChangePwd", "Confirm Password", None, QtGui.QApplication.UnicodeUTF8))

