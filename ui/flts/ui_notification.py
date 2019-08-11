# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_notification.ui'
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

class Ui_Notification_Dlg(object):
    def setupUi(self, Notification_Dlg):
        Notification_Dlg.setObjectName(_fromUtf8("Notification_Dlg"))
        Notification_Dlg.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Notification_Dlg)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tvw_notification = NotificationWidget(Notification_Dlg)
        self.tvw_notification.setObjectName(_fromUtf8("tvw_notification"))
        self.gridLayout.addWidget(self.tvw_notification, 0, 0, 1, 1)

        self.retranslateUi(Notification_Dlg)
        QtCore.QMetaObject.connectSlotsByName(Notification_Dlg)

    def retranslateUi(self, Notification_Dlg):
        Notification_Dlg.setWindowTitle(_translate("Notification_Dlg", "Notification Dialog", None))

from stdm.ui.customcontrols.notification_widget import NotificationWidget
