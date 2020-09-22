# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_doc_item.ui'
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

class Ui_frmDocumentItem(object):
    def setupUi(self, frmDocumentItem):
        frmDocumentItem.setObjectName(_fromUtf8("frmDocumentItem"))
        frmDocumentItem.resize(502, 64)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmDocumentItem.sizePolicy().hasHeightForWidth())
        frmDocumentItem.setSizePolicy(sizePolicy)
        frmDocumentItem.setMinimumSize(QtCore.QSize(50, 64))
        frmDocumentItem.setMaximumSize(QtCore.QSize(16777215, 64))
        frmDocumentItem.setStyleSheet(_fromUtf8(""))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(frmDocumentItem)
        self.horizontalLayout_2.setMargin(2)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.frame = QtGui.QFrame(frmDocumentItem)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(100, 60))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame.setStyleSheet(_fromUtf8("background-color: rgb(200, 200, 200);"))
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setMargin(5)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pgBar = QtGui.QProgressBar(self.frame)
        self.pgBar.setMinimumSize(QtCore.QSize(90, 16))
        self.pgBar.setMaximumSize(QtCore.QSize(90, 16))
        self.pgBar.setProperty("value", 24)
        self.pgBar.setObjectName(_fromUtf8("pgBar"))
        self.gridLayout.addWidget(self.pgBar, 0, 2, 1, 1)
        self.lblName = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        self.lblName.setMinimumSize(QtCore.QSize(20, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblName.setFont(font)
        self.lblName.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lblName.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblName.setText(_fromUtf8(""))
        self.lblName.setTextFormat(QtCore.Qt.RichText)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 1, 1, 1)
        self.lblClose = QtGui.QLabel(self.frame)
        self.lblClose.setMinimumSize(QtCore.QSize(16, 16))
        self.lblClose.setMaximumSize(QtCore.QSize(16, 16))
        self.lblClose.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.lblClose.setText(_fromUtf8(""))
        self.lblClose.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/close.png")))
        self.lblClose.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblClose.setObjectName(_fromUtf8("lblClose"))
        self.gridLayout.addWidget(self.lblClose, 0, 3, 1, 1)
        self.lblThumbnail = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblThumbnail.sizePolicy().hasHeightForWidth())
        self.lblThumbnail.setSizePolicy(sizePolicy)
        self.lblThumbnail.setMinimumSize(QtCore.QSize(48, 48))
        self.lblThumbnail.setMaximumSize(QtCore.QSize(48, 48))
        self.lblThumbnail.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblThumbnail.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblThumbnail.setText(_fromUtf8(""))
        self.lblThumbnail.setObjectName(_fromUtf8("lblThumbnail"))
        self.gridLayout.addWidget(self.lblThumbnail, 0, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(frmDocumentItem)
        QtCore.QMetaObject.connectSlotsByName(frmDocumentItem)

    def retranslateUi(self, frmDocumentItem):
        frmDocumentItem.setWindowTitle(_translate("frmDocumentItem", "Form", None))
        self.lblClose.setToolTip(_translate("frmDocumentItem", "Remove Document", None))

