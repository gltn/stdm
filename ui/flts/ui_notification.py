# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_notification.ui'
#
# Created: Mon Jul  8 13:24:51 2019
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_Notification_Dlg(object):
    def setupUi(self, Notification_Dlg):
        Notification_Dlg.setObjectName(_fromUtf8("Notification_Dlg"))
        Notification_Dlg.resize(400, 300)
        self.notification_Widget = QtGui.QListWidget(Notification_Dlg)
        self.notification_Widget.setGeometry(QtCore.QRect(10, 10, 381, 192))
        self.notification_Widget.setObjectName(_fromUtf8("notification_Widget"))
        self.pushButton = QtGui.QPushButton(Notification_Dlg)
        self.pushButton.setGeometry(QtCore.QRect(30, 230, 101, 31))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_2 = QtGui.QPushButton(Notification_Dlg)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 230, 101, 31))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))

        self.retranslateUi(Notification_Dlg)
        QtCore.QMetaObject.connectSlotsByName(Notification_Dlg)

    def retranslateUi(self, Notification_Dlg):
        Notification_Dlg.setWindowTitle(_translate("Notification_Dlg", "Dialog", None))
        self.pushButton.setText(_translate("Notification_Dlg", "Read", None))
        self.pushButton_2.setText(_translate("Notification_Dlg", "Send", None))

