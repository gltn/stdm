# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_notif_item.ui'
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

class Ui_frmNotificationItem(object):
    def setupUi(self, frmNotificationItem):
        frmNotificationItem.setObjectName(_fromUtf8("frmNotificationItem"))
        frmNotificationItem.resize(541, 35)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmNotificationItem.sizePolicy().hasHeightForWidth())
        frmNotificationItem.setSizePolicy(sizePolicy)
        frmNotificationItem.setMaximumSize(QtCore.QSize(16777215, 35))
        frmNotificationItem.setStyleSheet(_fromUtf8(""))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(frmNotificationItem)
        self.horizontalLayout_2.setMargin(2)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.frame = QtGui.QFrame(frmNotificationItem)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setSizeIncrement(QtCore.QSize(0, 20))
        self.frame.setStyleSheet(_fromUtf8("background-color: rgb(200, 200, 200);"))
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setMargin(5)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblNotifIcon = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblNotifIcon.sizePolicy().hasHeightForWidth())
        self.lblNotifIcon.setSizePolicy(sizePolicy)
        self.lblNotifIcon.setText(_fromUtf8(""))
        self.lblNotifIcon.setObjectName(_fromUtf8("lblNotifIcon"))
        self.horizontalLayout.addWidget(self.lblNotifIcon)
        self.lblNotifMessage = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblNotifMessage.sizePolicy().hasHeightForWidth())
        self.lblNotifMessage.setSizePolicy(sizePolicy)
        self.lblNotifMessage.setMinimumSize(QtCore.QSize(20, 20))
        self.lblNotifMessage.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.lblNotifMessage.setFont(font)
        self.lblNotifMessage.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.lblNotifMessage.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblNotifMessage.setText(_fromUtf8(""))
        self.lblNotifMessage.setTextFormat(QtCore.Qt.RichText)
        self.lblNotifMessage.setWordWrap(True)
        self.lblNotifMessage.setObjectName(_fromUtf8("lblNotifMessage"))
        self.horizontalLayout.addWidget(self.lblNotifMessage)
        self.lblClose = QtGui.QLabel(self.frame)
        self.lblClose.setMinimumSize(QtCore.QSize(5, 5))
        self.lblClose.setMaximumSize(QtCore.QSize(12, 12))
        self.lblClose.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lblClose.setText(_fromUtf8(""))
        self.lblClose.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/close_msg.png")))
        self.lblClose.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblClose.setWordWrap(False)
        self.lblClose.setObjectName(_fromUtf8("lblClose"))
        self.horizontalLayout.addWidget(self.lblClose)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(frmNotificationItem)
        QtCore.QMetaObject.connectSlotsByName(frmNotificationItem)

    def retranslateUi(self, frmNotificationItem):
        frmNotificationItem.setWindowTitle(_translate("frmNotificationItem", "Form", None))
        self.lblClose.setToolTip(_translate("frmNotificationItem", "Close Message", None))

from stdm import resources_rc
