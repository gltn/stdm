# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_admin_details.ui'
#
# Created: Fri Jun 07 21:16:02 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmAdminDetails(object):
    def setupUi(self, frmAdminDetails):
        frmAdminDetails.setObjectName(_fromUtf8("frmAdminDetails"))
        frmAdminDetails.resize(318, 180)
        self.gridLayout = QtGui.QGridLayout(frmAdminDetails)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gpAdminLevel = QtGui.QGroupBox(frmAdminDetails)
        self.gpAdminLevel.setTitle(_fromUtf8(""))
        self.gpAdminLevel.setObjectName(_fromUtf8("gpAdminLevel"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gpAdminLevel)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.gpAdminLevel)
        self.label.setMinimumSize(QtCore.QSize(50, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.txtName = QtGui.QLineEdit(self.gpAdminLevel)
        self.txtName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtName.setObjectName(_fromUtf8("txtName"))
        self.gridLayout_2.addWidget(self.txtName, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.gpAdminLevel)
        self.label_2.setMinimumSize(QtCore.QSize(50, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtCode = QtGui.QLineEdit(self.gpAdminLevel)
        self.txtCode.setMinimumSize(QtCore.QSize(0, 30))
        self.txtCode.setMaxLength(10)
        self.txtCode.setObjectName(_fromUtf8("txtCode"))
        self.gridLayout_2.addWidget(self.txtCode, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.gpAdminLevel, 0, 0, 1, 1)
        self.btnBoxAdminDetails = QtGui.QDialogButtonBox(frmAdminDetails)
        self.btnBoxAdminDetails.setOrientation(QtCore.Qt.Horizontal)
        self.btnBoxAdminDetails.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.btnBoxAdminDetails.setObjectName(_fromUtf8("btnBoxAdminDetails"))
        self.gridLayout.addWidget(self.btnBoxAdminDetails, 1, 0, 1, 1)

        self.retranslateUi(frmAdminDetails)
        QtCore.QObject.connect(self.btnBoxAdminDetails, QtCore.SIGNAL(_fromUtf8("rejected()")), frmAdminDetails.reject)
        QtCore.QMetaObject.connectSlotsByName(frmAdminDetails)

    def retranslateUi(self, frmAdminDetails):
        frmAdminDetails.setWindowTitle(QtGui.QApplication.translate("frmAdminDetails", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmAdminDetails", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmAdminDetails", "Code", None, QtGui.QApplication.UnicodeUTF8))

