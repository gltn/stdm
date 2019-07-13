# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_scheme_establishment.ui'
#
# Created: Fri Jul 12 17:21:57 2019
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

class Ui_scheme_establish_dialog(object):
    def setupUi(self, scheme_establish_dialog):
        scheme_establish_dialog.setObjectName(_fromUtf8("scheme_establish_dialog"))
        scheme_establish_dialog.resize(635, 470)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(scheme_establish_dialog.sizePolicy().hasHeightForWidth())
        scheme_establish_dialog.setSizePolicy(sizePolicy)
        scheme_establish_dialog.setMinimumSize(QtCore.QSize(500, 300))
        scheme_establish_dialog.setMaximumSize(QtCore.QSize(700, 1000))
        self.gridLayout_2 = QtGui.QGridLayout(scheme_establish_dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tw_lodgement_details = QtGui.QTreeView(scheme_establish_dialog)
        self.tw_lodgement_details.setMinimumSize(QtCore.QSize(0, 0))
        self.tw_lodgement_details.setMaximumSize(QtCore.QSize(16777215, 800))
        self.tw_lodgement_details.setObjectName(_fromUtf8("tw_lodgement_details"))
        self.gridLayout_2.addWidget(self.tw_lodgement_details, 1, 0, 1, 1)
        self.frame = QtGui.QFrame(scheme_establish_dialog)
        self.frame.setMinimumSize(QtCore.QSize(200, 45))
        self.frame.setMaximumSize(QtCore.QSize(600, 16777215))
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 131, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 471, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 2)
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
        self.gridLayout = QtGui.QGridLayout(self.frame_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chk_approve = QtGui.QCheckBox(self.frame_2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/approve.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chk_approve.setIcon(icon)
        self.chk_approve.setObjectName(_fromUtf8("chk_approve"))
        self.gridLayout.addWidget(self.chk_approve, 0, 0, 1, 1)
        self.chk_disapprove = QtGui.QCheckBox(self.frame_2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/disapprove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chk_disapprove.setIcon(icon1)
        self.chk_disapprove.setObjectName(_fromUtf8("chk_disapprove"))
        self.gridLayout.addWidget(self.chk_disapprove, 0, 1, 1, 1)
        self.closeBtn = QtGui.QPushButton(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.closeBtn.sizePolicy().hasHeightForWidth())
        self.closeBtn.setSizePolicy(sizePolicy)
        self.closeBtn.setMinimumSize(QtCore.QSize(70, 20))
        self.closeBtn.setMaximumSize(QtCore.QSize(60, 32))
        self.closeBtn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.closeBtn.setObjectName(_fromUtf8("closeBtn"))
        self.gridLayout.addWidget(self.closeBtn, 2, 1, 1, 1)
        self.textEdit_approval = QtGui.QTextEdit(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_approval.sizePolicy().hasHeightForWidth())
        self.textEdit_approval.setSizePolicy(sizePolicy)
        self.textEdit_approval.setMinimumSize(QtCore.QSize(0, 0))
        self.textEdit_approval.setMaximumSize(QtCore.QSize(16777215, 600))
        self.textEdit_approval.setSizeIncrement(QtCore.QSize(0, 450))
        self.textEdit_approval.setObjectName(_fromUtf8("textEdit_approval"))
        self.gridLayout.addWidget(self.textEdit_approval, 1, 0, 1, 2)
        self.gridLayout_2.addWidget(self.frame_2, 1, 1, 1, 1)

        self.retranslateUi(scheme_establish_dialog)
        QtCore.QObject.connect(self.closeBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), scheme_establish_dialog.close)
        QtCore.QMetaObject.connectSlotsByName(scheme_establish_dialog)

    def retranslateUi(self, scheme_establish_dialog):
        scheme_establish_dialog.setWindowTitle(_translate("scheme_establish_dialog", "Establishment of Scheme", None))
        self.label.setText(_translate("scheme_establish_dialog", "Scheme establishment", None))
        self.label_2.setText(_translate("scheme_establish_dialog", "Please review the scheme information below for approval or disapproval with comments attached", None))
        self.chk_approve.setText(_translate("scheme_establish_dialog", "Approve", None))
        self.chk_disapprove.setText(_translate("scheme_establish_dialog", "Disapprove", None))
        self.closeBtn.setText(_translate("scheme_establish_dialog", "Submit", None))

# import resources_rc
