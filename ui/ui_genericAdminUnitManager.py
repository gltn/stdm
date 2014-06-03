# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_genericAdminUnitManager.ui'
#
# Created: Sat Mar 08 10:15:29 2014
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

class Ui_frmAdminUnitDialog(object):
    def setupUi(self, frmAdminUnitDialog):
        frmAdminUnitDialog.setObjectName(_fromUtf8("frmAdminUnitDialog"))
        frmAdminUnitDialog.resize(406, 476)
        self.gridLayout = QtGui.QGridLayout(frmAdminUnitDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.adminUnitManager = AdminUnitManager(frmAdminUnitDialog)
        self.adminUnitManager.setObjectName(_fromUtf8("adminUnitManager"))
        self.gridLayout.addWidget(self.adminUnitManager, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmAdminUnitDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(frmAdminUnitDialog)
        QtCore.QMetaObject.connectSlotsByName(frmAdminUnitDialog)

    def retranslateUi(self, frmAdminUnitDialog):
        frmAdminUnitDialog.setWindowTitle(_translate("frmAdminUnitDialog", "Administrative Units Viewer", None))

from admin_unit_manager import AdminUnitManager
