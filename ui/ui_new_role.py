# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_new_role.ui'
#
# Created: Thu Jun 20 13:08:08 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmNewRole(object):
    def setupUi(self, frmNewRole):
        frmNewRole.setObjectName(_fromUtf8("frmNewRole"))
        frmNewRole.resize(280, 186)
        self.gridLayout = QtGui.QGridLayout(frmNewRole)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(frmNewRole)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.txtRoleName = QtGui.QLineEdit(self.groupBox)
        self.txtRoleName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtRoleName.setMaxLength(50)
        self.txtRoleName.setObjectName(_fromUtf8("txtRoleName"))
        self.gridLayout_2.addWidget(self.txtRoleName, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtRoleDescription = QtGui.QLineEdit(self.groupBox)
        self.txtRoleDescription.setMinimumSize(QtCore.QSize(0, 30))
        self.txtRoleDescription.setMaxLength(50)
        self.txtRoleDescription.setObjectName(_fromUtf8("txtRoleDescription"))
        self.gridLayout_2.addWidget(self.txtRoleDescription, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmNewRole)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(frmNewRole)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmNewRole.reject)
        QtCore.QMetaObject.connectSlotsByName(frmNewRole)

    def retranslateUi(self, frmNewRole):
        frmNewRole.setWindowTitle(QtGui.QApplication.translate("frmNewRole", "New Role", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("frmNewRole", "Role Information:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmNewRole", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmNewRole", "Description", None, QtGui.QApplication.UnicodeUTF8))

