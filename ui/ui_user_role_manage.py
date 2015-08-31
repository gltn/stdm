# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_user_role_manage.ui'
#
# Created: Wed Jul 08 17:54:46 2015
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

class Ui_frmSysManageAccounts(object):
    def setupUi(self, frmSysManageAccounts):
        frmSysManageAccounts.setObjectName(_fromUtf8("frmSysManageAccounts"))
        frmSysManageAccounts.resize(434, 380)
        self.gridLayout = QtGui.QGridLayout(frmSysManageAccounts)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(frmSysManageAccounts)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.tbUserRole = QtGui.QTabWidget(frmSysManageAccounts)
        self.tbUserRole.setObjectName(_fromUtf8("tbUserRole"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lstUsers = QtGui.QListView(self.tab)
        self.lstUsers.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstUsers.setAlternatingRowColors(True)
        self.lstUsers.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.lstUsers.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstUsers.setObjectName(_fromUtf8("lstUsers"))
        self.gridLayout_2.addWidget(self.lstUsers, 0, 0, 1, 1)
        self.btnManageUsers = QtGui.QDialogButtonBox(self.tab)
        self.btnManageUsers.setOrientation(QtCore.Qt.Vertical)
        self.btnManageUsers.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Save)
        self.btnManageUsers.setObjectName(_fromUtf8("btnManageUsers"))
        self.gridLayout_2.addWidget(self.btnManageUsers, 0, 1, 1, 1)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/user.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tbUserRole.addTab(self.tab, icon, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lstRoles = QtGui.QListView(self.tab_2)
        self.lstRoles.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstRoles.setAlternatingRowColors(True)
        self.lstRoles.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.lstRoles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstRoles.setObjectName(_fromUtf8("lstRoles"))
        self.gridLayout_3.addWidget(self.lstRoles, 0, 0, 1, 1)
        self.btnManageRoles = QtGui.QDialogButtonBox(self.tab_2)
        self.btnManageRoles.setOrientation(QtCore.Qt.Vertical)
        self.btnManageRoles.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.btnManageRoles.setObjectName(_fromUtf8("btnManageRoles"))
        self.gridLayout_3.addWidget(self.btnManageRoles, 0, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.tab_2)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 30))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.lblRoleDescription = QtGui.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblRoleDescription.setFont(font)
        self.lblRoleDescription.setText(_fromUtf8(""))
        self.lblRoleDescription.setObjectName(_fromUtf8("lblRoleDescription"))
        self.gridLayout_4.addWidget(self.lblRoleDescription, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 1, 0, 1, 1)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/roles.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tbUserRole.addTab(self.tab_2, icon1, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_3)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label = QtGui.QLabel(self.tab_3)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_5.addWidget(self.label, 0, 0, 1, 2)
        self.lstMappingRoles = QtGui.QListView(self.tab_3)
        self.lstMappingRoles.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstMappingRoles.setAlternatingRowColors(True)
        self.lstMappingRoles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstMappingRoles.setObjectName(_fromUtf8("lstMappingRoles"))
        self.gridLayout_5.addWidget(self.lstMappingRoles, 1, 0, 1, 1)
        self.lstMappingUsers = QtGui.QListView(self.tab_3)
        self.lstMappingUsers.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstMappingUsers.setAlternatingRowColors(True)
        self.lstMappingUsers.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstMappingUsers.setObjectName(_fromUtf8("lstMappingUsers"))
        self.gridLayout_5.addWidget(self.lstMappingUsers, 1, 1, 1, 1)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/user_mapping.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tbUserRole.addTab(self.tab_3, icon2, _fromUtf8(""))
        self.gridLayout.addWidget(self.tbUserRole, 1, 0, 1, 1)

        self.retranslateUi(frmSysManageAccounts)
        self.tbUserRole.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmSysManageAccounts.close)
        QtCore.QMetaObject.connectSlotsByName(frmSysManageAccounts)

    def retranslateUi(self, frmSysManageAccounts):
        frmSysManageAccounts.setWindowTitle(_translate("frmSysManageAccounts", "Manage System Users and Roles", None))
        self.tbUserRole.setTabText(self.tbUserRole.indexOf(self.tab), _translate("frmSysManageAccounts", "Users", None))
        self.groupBox.setTitle(_translate("frmSysManageAccounts", "Description:", None))
        self.tbUserRole.setTabText(self.tbUserRole.indexOf(self.tab_2), _translate("frmSysManageAccounts", "Roles", None))
        self.label.setText(_translate("frmSysManageAccounts", "<html><head/><body><p>Click on a role in the table on the left-hand side below then check/uncheck the users in the table on the right-hand side to add/remove them in this role.</p></body></html>", None))
        self.tbUserRole.setTabText(self.tbUserRole.indexOf(self.tab_3), _translate("frmSysManageAccounts", "Mappings", None))
