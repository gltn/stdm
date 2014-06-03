# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_new_user.ui'
#
# Created: Thu Jun 20 09:29:14 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmNewUser(object):
    def setupUi(self, frmNewUser):
        frmNewUser.setObjectName(_fromUtf8("frmNewUser"))
        frmNewUser.resize(333, 276)
        self.gridLayout_2 = QtGui.QGridLayout(frmNewUser)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(frmNewUser)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtConfirmPass = QtGui.QLineEdit(self.groupBox)
        self.txtConfirmPass.setMinimumSize(QtCore.QSize(0, 30))
        self.txtConfirmPass.setMaxLength(50)
        self.txtConfirmPass.setEchoMode(QtGui.QLineEdit.Password)
        self.txtConfirmPass.setObjectName(_fromUtf8("txtConfirmPass"))
        self.gridLayout.addWidget(self.txtConfirmPass, 2, 1, 1, 1)
        self.dtValidity = QtGui.QDateEdit(self.groupBox)
        self.dtValidity.setEnabled(False)
        self.dtValidity.setMinimumSize(QtCore.QSize(0, 30))
        self.dtValidity.setCalendarPopup(True)
        self.dtValidity.setObjectName(_fromUtf8("dtValidity"))
        self.gridLayout.addWidget(self.dtValidity, 3, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.txtPass = QtGui.QLineEdit(self.groupBox)
        self.txtPass.setMinimumSize(QtCore.QSize(0, 30))
        self.txtPass.setMaxLength(50)
        self.txtPass.setEchoMode(QtGui.QLineEdit.Password)
        self.txtPass.setObjectName(_fromUtf8("txtPass"))
        self.gridLayout.addWidget(self.txtPass, 1, 1, 1, 1)
        self.txtUserName = QtGui.QLineEdit(self.groupBox)
        self.txtUserName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtUserName.setMaxLength(50)
        self.txtUserName.setObjectName(_fromUtf8("txtUserName"))
        self.gridLayout.addWidget(self.txtUserName, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.chkValidity = QtGui.QCheckBox(self.groupBox)
        self.chkValidity.setChecked(True)
        self.chkValidity.setObjectName(_fromUtf8("chkValidity"))
        self.gridLayout.addWidget(self.chkValidity, 4, 0, 1, 2)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmNewUser)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(frmNewUser)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmNewUser.reject)
        QtCore.QMetaObject.connectSlotsByName(frmNewUser)
        frmNewUser.setTabOrder(self.txtUserName, self.txtPass)
        frmNewUser.setTabOrder(self.txtPass, self.txtConfirmPass)
        frmNewUser.setTabOrder(self.txtConfirmPass, self.dtValidity)
        frmNewUser.setTabOrder(self.dtValidity, self.chkValidity)
        frmNewUser.setTabOrder(self.chkValidity, self.buttonBox)

    def retranslateUi(self, frmNewUser):
        frmNewUser.setWindowTitle(QtGui.QApplication.translate("frmNewUser", "New User Account", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("frmNewUser", "New User Information:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("frmNewUser", "Confirm Password", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmNewUser", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("frmNewUser", "Account Expires On", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmNewUser", "UserName", None, QtGui.QApplication.UnicodeUTF8))
        self.chkValidity.setText(QtGui.QApplication.translate("frmNewUser", "No Expiry Date", None, QtGui.QApplication.UnicodeUTF8))

