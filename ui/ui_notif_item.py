# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_notif_item.ui'
#
# Created: Tue Oct 01 09:55:14 2013
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

class Ui_frmNotificationItem(object):
    def setupUi(self, frmNotificationItem):
        frmNotificationItem.setObjectName(_fromUtf8("frmNotificationItem"))
        frmNotificationItem.resize(541, 35)
        frmNotificationItem.setMaximumSize(QtCore.QSize(16777215, 35))
        frmNotificationItem.setStyleSheet(_fromUtf8(""))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(frmNotificationItem)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setMargin(2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.frame = QtGui.QFrame(frmNotificationItem)
        self.frame.setStyleSheet(_fromUtf8("background-color: rgb(200, 200, 200);"))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setMargin(5)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblNotifIcon = QtGui.QLabel(self.frame)
        self.lblNotifIcon.setText(_fromUtf8(""))
        self.lblNotifIcon.setObjectName(_fromUtf8("lblNotifIcon"))
        self.gridLayout.addWidget(self.lblNotifIcon, 0, 0, 1, 1)
        self.lblNotifMessage = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblNotifMessage.sizePolicy().hasHeightForWidth())
        self.lblNotifMessage.setSizePolicy(sizePolicy)
        self.lblNotifMessage.setMinimumSize(QtCore.QSize(20, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.lblNotifMessage.setFont(font)
        self.lblNotifMessage.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.lblNotifMessage.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblNotifMessage.setText(_fromUtf8(""))
        self.lblNotifMessage.setTextFormat(QtCore.Qt.RichText)
        self.lblNotifMessage.setObjectName(_fromUtf8("lblNotifMessage"))
        self.gridLayout.addWidget(self.lblNotifMessage, 0, 1, 1, 1)
        self.lblClose = QtGui.QLabel(self.frame)
        self.lblClose.setMinimumSize(QtCore.QSize(16, 16))
        self.lblClose.setMaximumSize(QtCore.QSize(16, 16))
        self.lblClose.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lblClose.setText(_fromUtf8(""))
        self.lblClose.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/close.png")))
        self.lblClose.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblClose.setObjectName(_fromUtf8("lblClose"))
        self.gridLayout.addWidget(self.lblClose, 0, 2, 1, 1)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(frmNotificationItem)
        QtCore.QMetaObject.connectSlotsByName(frmNotificationItem)

    def retranslateUi(self, frmNotificationItem):
        frmNotificationItem.setWindowTitle(_translate("frmNotificationItem", "Form", None))
        self.lblClose.setToolTip(_translate("frmNotificationItem", "Close Message", None))

