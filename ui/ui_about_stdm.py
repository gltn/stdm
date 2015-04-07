# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about_stdm.ui'
#
# Created: Thu Jun 26 16:51:51 2014
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

class Ui_frmAbout(object):
    def setupUi(self, frmAbout):
        frmAbout.setObjectName(_fromUtf8("frmAbout"))
        frmAbout.resize(613, 474)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmAbout.sizePolicy().hasHeightForWidth())
        frmAbout.setSizePolicy(sizePolicy)
        frmAbout.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayout = QtGui.QGridLayout(frmAbout)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtAbout = QtGui.QTextEdit(frmAbout)
        self.txtAbout.setReadOnly(True)
        self.txtAbout.setObjectName(_fromUtf8("txtAbout"))
        self.gridLayout.addWidget(self.txtAbout, 0, 0, 1, 2)
        self.btnSTDMHome = QtGui.QPushButton(frmAbout)
        self.btnSTDMHome.setMinimumSize(QtCore.QSize(0, 30))
        self.btnSTDMHome.setObjectName(_fromUtf8("btnSTDMHome"))
        self.gridLayout.addWidget(self.btnSTDMHome, 1, 0, 1, 1)
        self.btnContactUs = QtGui.QPushButton(frmAbout)
        self.btnContactUs.setMinimumSize(QtCore.QSize(0, 30))
        self.btnContactUs.setObjectName(_fromUtf8("btnContactUs"))
        self.gridLayout.addWidget(self.btnContactUs, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmAbout)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi(frmAbout)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmAbout.reject)
        QtCore.QMetaObject.connectSlotsByName(frmAbout)

    def retranslateUi(self, frmAbout):
        frmAbout.setWindowTitle(_translate("frmAbout", "About STDM", None))
        self.btnSTDMHome.setText(_translate("frmAbout", "STDM Home Page", None))
        self.btnContactUs.setText(_translate("frmAbout", "Contact Us", None))
