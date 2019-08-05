# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_scheme_establishment.ui'
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

class Ui_scheme_establish_dialog(object):
    def setupUi(self, scheme_establish_dialog):
        scheme_establish_dialog.setObjectName(_fromUtf8("scheme_establish_dialog"))
        scheme_establish_dialog.resize(802, 538)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(scheme_establish_dialog.sizePolicy().hasHeightForWidth())
        scheme_establish_dialog.setSizePolicy(sizePolicy)
        scheme_establish_dialog.setMinimumSize(QtCore.QSize(700, 300))
        scheme_establish_dialog.setMaximumSize(QtCore.QSize(1000, 1000))
        self.gridLayout = QtGui.QGridLayout(scheme_establish_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setContentsMargins(-1, -1, -1, 10)
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 3)
        self.tw_lodgement_details = SchemeSummaryWidget(scheme_establish_dialog)
        self.tw_lodgement_details.setMinimumSize(QtCore.QSize(0, 0))
        self.tw_lodgement_details.setMaximumSize(QtCore.QSize(16777215, 800))
        self.tw_lodgement_details.setObjectName(_fromUtf8("tw_lodgement_details"))
        self.gridLayout.addWidget(self.tw_lodgement_details, 2, 1, 1, 1)
        self.frame = QtGui.QFrame(scheme_establish_dialog)
        self.frame.setMinimumSize(QtCore.QSize(200, 30))
        self.frame.setMaximumSize(QtCore.QSize(600, 30))
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.lbl_Instruct = QtGui.QLabel(self.frame)
        self.lbl_Instruct.setGeometry(QtCore.QRect(10, 0, 465, 13))
        self.lbl_Instruct.setObjectName(_fromUtf8("lbl_Instruct"))
        self.gridLayout.addWidget(self.frame, 1, 0, 1, 3)
        self.frame_2 = QtGui.QFrame(scheme_establish_dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setSizeIncrement(QtCore.QSize(0, 0))
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.txtEdit_disApprv = QtGui.QTextEdit(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtEdit_disApprv.sizePolicy().hasHeightForWidth())
        self.txtEdit_disApprv.setSizePolicy(sizePolicy)
        self.txtEdit_disApprv.setMinimumSize(QtCore.QSize(0, 0))
        self.txtEdit_disApprv.setMaximumSize(QtCore.QSize(16777215, 600))
        self.txtEdit_disApprv.setSizeIncrement(QtCore.QSize(0, 450))
        self.txtEdit_disApprv.setObjectName(_fromUtf8("txtEdit_disApprv"))
        self.gridLayout_2.addWidget(self.txtEdit_disApprv, 1, 0, 1, 2)
        self.btnSubmit = QtGui.QPushButton(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSubmit.sizePolicy().hasHeightForWidth())
        self.btnSubmit.setSizePolicy(sizePolicy)
        self.btnSubmit.setMinimumSize(QtCore.QSize(70, 20))
        self.btnSubmit.setMaximumSize(QtCore.QSize(60, 32))
        self.btnSubmit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btnSubmit.setObjectName(_fromUtf8("btnSubmit"))
        self.gridLayout_2.addWidget(self.btnSubmit, 2, 1, 1, 1)
        self.chk_disapprove = QtGui.QCheckBox(self.frame_2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/disapprove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chk_disapprove.setIcon(icon)
        self.chk_disapprove.setObjectName(_fromUtf8("chk_disapprove"))
        self.gridLayout_2.addWidget(self.chk_disapprove, 0, 1, 1, 1)
        self.chk_approve = QtGui.QCheckBox(self.frame_2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/approve.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chk_approve.setIcon(icon1)
        self.chk_approve.setObjectName(_fromUtf8("chk_approve"))
        self.gridLayout_2.addWidget(self.chk_approve, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame_2, 2, 2, 1, 1)

        self.retranslateUi(scheme_establish_dialog)
        QtCore.QMetaObject.connectSlotsByName(scheme_establish_dialog)

    def retranslateUi(self, scheme_establish_dialog):
        scheme_establish_dialog.setWindowTitle(_translate("scheme_establish_dialog", "Establishment of Scheme", None))
        self.lbl_Instruct.setText(_translate("scheme_establish_dialog", "Please review the scheme information below for approval or disapproval with comments attached", None))
        self.btnSubmit.setText(_translate("scheme_establish_dialog", "Submit", None))
        self.chk_disapprove.setText(_translate("scheme_establish_dialog", "Disapprove", None))
        self.chk_approve.setText(_translate("scheme_establish_dialog", "Approve", None))

from stdm.ui.customcontrols.scheme_summary_widget import SchemeSummaryWidget
from stdm import resources_rc
