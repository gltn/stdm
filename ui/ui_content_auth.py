# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_content_auth.ui'
#
# Created: Mon Jul 01 10:52:55 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmContentAuth(object):
    def setupUi(self, frmContentAuth):
        frmContentAuth.setObjectName(_fromUtf8("frmContentAuth"))
        frmContentAuth.resize(501, 382)
        self.gridLayout = QtGui.QGridLayout(frmContentAuth)
        self.gridLayout.setContentsMargins(10, 12, 10, 10)
        self.gridLayout.setHorizontalSpacing(12)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(frmContentAuth)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.lstContent = QtGui.QListView(frmContentAuth)
        self.lstContent.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstContent.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstContent.setObjectName(_fromUtf8("lstContent"))
        self.gridLayout.addWidget(self.lstContent, 1, 0, 1, 1)
        self.lstRoles = QtGui.QListView(frmContentAuth)
        self.lstRoles.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstRoles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstRoles.setObjectName(_fromUtf8("lstRoles"))
        self.gridLayout.addWidget(self.lstRoles, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmContentAuth)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi(frmContentAuth)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmContentAuth.reject)
        QtCore.QMetaObject.connectSlotsByName(frmContentAuth)

    def retranslateUi(self, frmContentAuth):
        frmContentAuth.setWindowTitle(QtGui.QApplication.translate("frmContentAuth", "Content Authorization", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmContentAuth", "<html><head/><body><p>Click on a content item in the table on the left-hand side and check/uncheck to approve/disapprove the authorised roles on the table in the right-hand side below.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

