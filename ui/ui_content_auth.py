# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_content_auth.ui'
#
# Created: Tue Jan 28 11:57:18 2020
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_frmContentAuth(object):
    def setupUi(self, frmContentAuth):
        frmContentAuth.setObjectName(_fromUtf8("frmContentAuth"))
        frmContentAuth.resize(501, 382)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/flts_content_auth.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmContentAuth.setWindowIcon(icon)
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
        frmContentAuth.setWindowTitle(_translate("frmContentAuth", "Content Authorization", None))
        self.label.setText(_translate("frmContentAuth", "<html><head/><body><p>Click on a content item in the table on the left-hand side and check/uncheck to approve/disapprove the authorised roles on the table in the right-hand side below.</p></body></html>", None))

from stdm import resources_rc
