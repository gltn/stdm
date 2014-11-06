# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_login.ui'
#
# Created: Tue Feb 18 17:45:33 2014
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

class Ui_frmLogin(object):
    def setupUi(self, frmLogin):
        frmLogin.setObjectName(_fromUtf8("frmLogin"))
        frmLogin.resize(320, 208)
        frmLogin.setMaximumSize(QtCore.QSize(320, 16777215))
        self.gridLayout_2 = QtGui.QGridLayout(frmLogin)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtUserName = QtGui.QLineEdit(frmLogin)
        self.txtUserName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtUserName.setObjectName(_fromUtf8("txtUserName"))
        self.gridLayout.addWidget(self.txtUserName, 0, 1, 1, 1)
        self.label = QtGui.QLabel(frmLogin)
        self.label.setMinimumSize(QtCore.QSize(70, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(frmLogin)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtPassword = QtGui.QLineEdit(frmLogin)
        self.txtPassword.setMinimumSize(QtCore.QSize(0, 30))
        self.txtPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.txtPassword.setObjectName(_fromUtf8("txtPassword"))
        self.gridLayout.addWidget(self.txtPassword, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.btnBox = QtGui.QDialogButtonBox(frmLogin)
        self.btnBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.btnBox.setObjectName(_fromUtf8("btnBox"))
        self.gridLayout_2.addWidget(self.btnBox, 2, 0, 1, 1)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout_2.addLayout(self.vlNotification, 0, 0, 1, 1)

        self.retranslateUi(frmLogin)
        QtCore.QObject.connect(self.btnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmLogin.reject)
        QtCore.QMetaObject.connectSlotsByName(frmLogin)
        frmLogin.setTabOrder(self.txtUserName, self.txtPassword)
        frmLogin.setTabOrder(self.txtPassword, self.btnBox)

    def retranslateUi(self, frmLogin):
        frmLogin.setWindowTitle(_translate("frmLogin", "STDM Login", None))
        self.label.setText(_translate("frmLogin", "UserName", None))
        self.label_2.setText(_translate("frmLogin", "Password", None))

