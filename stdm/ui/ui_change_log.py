# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_change_log.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_ChangeLog(object):
    def setupUi(self, ChangeLog):
        ChangeLog.setObjectName(_fromUtf8("ChangeLog"))
        ChangeLog.resize(714, 557)
        self.verticalLayout = QtGui.QVBoxLayout(ChangeLog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.webView = QtWebKit.QWebView(ChangeLog)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.verticalLayout.addWidget(self.webView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ChangeLog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        spacerItem = QtGui.QSpacerItem(600000, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ChangeLog)
        QtCore.QMetaObject.connectSlotsByName(ChangeLog)

    def retranslateUi(self, ChangeLog):
        ChangeLog.setWindowTitle(_translate("ChangeLog", "What is New?", None))

from PyQt4 import QtWebKit
