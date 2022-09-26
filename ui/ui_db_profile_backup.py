# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_db_profile_backup.ui'
#
# Created: Sun Sep 18 14:20:50 2022
#      by: PyQt4 UI code generator 4.10
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

class Ui_dlgDBProfileBackup(object):
    def setupUi(self, dlgDBProfileBackup):
        dlgDBProfileBackup.setObjectName(_fromUtf8("dlgDBProfileBackup"))
        dlgDBProfileBackup.resize(522, 344)
        self.verticalLayout = QtGui.QVBoxLayout(dlgDBProfileBackup)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(dlgDBProfileBackup)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.label_4 = QtGui.QLabel(dlgDBProfileBackup)
        self.label_4.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.txtDBName = QtGui.QLabel(dlgDBProfileBackup)
        self.txtDBName.setObjectName(_fromUtf8("txtDBName"))
        self.gridLayout.addWidget(self.txtDBName, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(dlgDBProfileBackup)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(dlgDBProfileBackup)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.edtBackupFolder = QtGui.QLineEdit(dlgDBProfileBackup)
        self.edtBackupFolder.setReadOnly(True)
        self.edtBackupFolder.setObjectName(_fromUtf8("edtBackupFolder"))
        self.gridLayout.addWidget(self.edtBackupFolder, 4, 1, 1, 1)
        self.tbBackupFolder = QtGui.QToolButton(dlgDBProfileBackup)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/open_file.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tbBackupFolder.setIcon(icon)
        self.tbBackupFolder.setObjectName(_fromUtf8("tbBackupFolder"))
        self.gridLayout.addWidget(self.tbBackupFolder, 4, 2, 1, 1)
        self.label_5 = QtGui.QLabel(dlgDBProfileBackup)
        self.label_5.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.edtAdminPassword = QtGui.QLineEdit(dlgDBProfileBackup)
        self.edtAdminPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.edtAdminPassword.setObjectName(_fromUtf8("edtAdminPassword"))
        self.gridLayout.addWidget(self.edtAdminPassword, 3, 1, 1, 1)
        self.txtAdmin = QtGui.QLabel(dlgDBProfileBackup)
        self.txtAdmin.setObjectName(_fromUtf8("txtAdmin"))
        self.gridLayout.addWidget(self.txtAdmin, 2, 1, 1, 1)
        self.lwProfiles = QtGui.QListWidget(dlgDBProfileBackup)
        self.lwProfiles.setMaximumSize(QtCore.QSize(16777215, 100))
        self.lwProfiles.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lwProfiles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lwProfiles.setObjectName(_fromUtf8("lwProfiles"))
        self.gridLayout.addWidget(self.lwProfiles, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(dlgDBProfileBackup)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.cbCompress = QtGui.QCheckBox(dlgDBProfileBackup)
        self.cbCompress.setText(_fromUtf8(""))
        self.cbCompress.setObjectName(_fromUtf8("cbCompress"))
        self.gridLayout.addWidget(self.cbCompress, 5, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.line = QtGui.QFrame(dlgDBProfileBackup)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnBackup = QtGui.QPushButton(dlgDBProfileBackup)
        self.btnBackup.setObjectName(_fromUtf8("btnBackup"))
        self.horizontalLayout.addWidget(self.btnBackup)
        self.btnOpenFolder = QtGui.QPushButton(dlgDBProfileBackup)
        self.btnOpenFolder.setObjectName(_fromUtf8("btnOpenFolder"))
        self.horizontalLayout.addWidget(self.btnOpenFolder)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(dlgDBProfileBackup)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.horizontalLayout.addWidget(self.btnClose)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(dlgDBProfileBackup)
        QtCore.QMetaObject.connectSlotsByName(dlgDBProfileBackup)

    def retranslateUi(self, dlgDBProfileBackup):
        dlgDBProfileBackup.setWindowTitle(_translate("dlgDBProfileBackup", "Profile Configuration & Database Backup", None))
        self.label.setText(_translate("dlgDBProfileBackup", "Backup Folder:", None))
        self.label_4.setText(_translate("dlgDBProfileBackup", "Database Admin:", None))
        self.txtDBName.setText(_translate("dlgDBProfileBackup", "TextLabel", None))
        self.label_3.setText(_translate("dlgDBProfileBackup", "Database Name:", None))
        self.label_2.setText(_translate("dlgDBProfileBackup", "Profile(s):", None))
        self.tbBackupFolder.setText(_translate("dlgDBProfileBackup", "...", None))
        self.label_5.setText(_translate("dlgDBProfileBackup", "Admin Password:", None))
        self.txtAdmin.setText(_translate("dlgDBProfileBackup", "TextLabel", None))
        self.label_6.setText(_translate("dlgDBProfileBackup", "Make ZIP Package:", None))
        self.btnBackup.setText(_translate("dlgDBProfileBackup", "Backup Data", None))
        self.btnOpenFolder.setText(_translate("dlgDBProfileBackup", "Open Backup Folder", None))
        self.btnClose.setText(_translate("dlgDBProfileBackup", "Close", None))

