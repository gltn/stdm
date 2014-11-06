# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dbconn.ui'
#
# Created: Mon May 27 11:59:09 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmDbConn(object):
    def setupUi(self, frmDbConn):
        frmDbConn.setObjectName(_fromUtf8("frmDbConn"))
        frmDbConn.resize(320, 208)
        frmDbConn.setMaximumSize(QtCore.QSize(320, 16777215))
        self.gridLayout_2 = QtGui.QGridLayout(frmDbConn)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtHost = QtGui.QLineEdit(frmDbConn)
        self.txtHost.setMinimumSize(QtCore.QSize(0, 30))
        self.txtHost.setMaxLength(200)
        self.txtHost.setObjectName(_fromUtf8("txtHost"))
        self.gridLayout.addWidget(self.txtHost, 0, 1, 1, 1)
        self.label = QtGui.QLabel(frmDbConn)
        self.label.setMinimumSize(QtCore.QSize(70, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(frmDbConn)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtPort = QtGui.QLineEdit(frmDbConn)
        self.txtPort.setMinimumSize(QtCore.QSize(0, 30))
        self.txtPort.setMaxLength(6)
        self.txtPort.setEchoMode(QtGui.QLineEdit.Normal)
        self.txtPort.setObjectName(_fromUtf8("txtPort"))
        self.gridLayout.addWidget(self.txtPort, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(frmDbConn)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.txtDatabase = QtGui.QLineEdit(frmDbConn)
        self.txtDatabase.setMinimumSize(QtCore.QSize(0, 30))
        self.txtDatabase.setMaxLength(100)
        self.txtDatabase.setObjectName(_fromUtf8("txtDatabase"))
        self.gridLayout.addWidget(self.txtDatabase, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.btnBox = QtGui.QDialogButtonBox(frmDbConn)
        self.btnBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.btnBox.setObjectName(_fromUtf8("btnBox"))
        self.gridLayout_2.addWidget(self.btnBox, 1, 0, 1, 1)

        self.retranslateUi(frmDbConn)
        QtCore.QObject.connect(self.btnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmDbConn.reject)
        QtCore.QMetaObject.connectSlotsByName(frmDbConn)

    def retranslateUi(self, frmDbConn):
        frmDbConn.setWindowTitle(QtGui.QApplication.translate("frmDbConn", "PostgreSQL Database Connection", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmDbConn", "Host", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmDbConn", "Port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("frmDbConn", "Database", None, QtGui.QApplication.UnicodeUTF8))

