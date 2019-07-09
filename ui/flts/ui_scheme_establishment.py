# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_scheme_establishment.ui'
#
# Created: Tue Jul  9 06:17:10 2019
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
        scheme_establish_dialog.resize(609, 456)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(scheme_establish_dialog.sizePolicy().hasHeightForWidth())
        scheme_establish_dialog.setSizePolicy(sizePolicy)
        scheme_establish_dialog.setMinimumSize(QtCore.QSize(600, 0))
        scheme_establish_dialog.setMaximumSize(QtCore.QSize(800, 900))
        self.gridLayout_4 = QtGui.QGridLayout(scheme_establish_dialog)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.scrollArea = QtGui.QScrollArea(scheme_establish_dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Plain)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 293, 387))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.textEdit_2 = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy)
        self.textEdit_2.setFrameShadow(QtGui.QFrame.Raised)
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setObjectName(_fromUtf8("textEdit_2"))
        self.gridLayout_2.addWidget(self.textEdit_2, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_4.addWidget(self.scrollArea, 1, 0, 3, 1)
        self.frame_2 = QtGui.QFrame(scheme_establish_dialog)
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout = QtGui.QGridLayout(self.frame_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.checkBox_2 = QtGui.QCheckBox(self.frame_2)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.gridLayout.addWidget(self.checkBox_2, 0, 1, 1, 1)
        self.textEdit = QtGui.QTextEdit(self.frame_2)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 2)
        self.checkBox = QtGui.QCheckBox(self.frame_2)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 2)
        self.gridLayout_4.addWidget(self.frame_2, 1, 1, 1, 1)
        self.frame = QtGui.QFrame(scheme_establish_dialog)
        self.frame.setMinimumSize(QtCore.QSize(200, 45))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
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
        self.gridLayout_4.addWidget(self.frame, 0, 0, 1, 2)
        self.frame_4 = QtGui.QFrame(scheme_establish_dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy)
        self.frame_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame_4.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_4.setObjectName(_fromUtf8("frame_4"))
        self.gridLayout_5 = QtGui.QGridLayout(self.frame_4)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_5 = QtGui.QLabel(self.frame_4)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_5.addWidget(self.label_5, 0, 0, 1, 1)
        self.closeBtn = QtGui.QPushButton(self.frame_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.closeBtn.sizePolicy().hasHeightForWidth())
        self.closeBtn.setSizePolicy(sizePolicy)
        self.closeBtn.setMinimumSize(QtCore.QSize(100, 30))
        self.closeBtn.setMaximumSize(QtCore.QSize(60, 30))
        self.closeBtn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.closeBtn.setObjectName(_fromUtf8("closeBtn"))
        self.gridLayout_5.addWidget(self.closeBtn, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.frame_4, 2, 1, 1, 1)

        self.retranslateUi(scheme_establish_dialog)
        QtCore.QObject.connect(self.closeBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), scheme_establish_dialog.close)
        QtCore.QMetaObject.connectSlotsByName(scheme_establish_dialog)

    def retranslateUi(self, scheme_establish_dialog):
        scheme_establish_dialog.setWindowTitle(_translate("scheme_establish_dialog", "Establishment of Scheme", None))
        self.textEdit_2.setHtml(_translate("scheme_establish_dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>", None))
        self.checkBox_2.setText(_translate("scheme_establish_dialog", "Disapprove", None))
        self.textEdit.setHtml(_translate("scheme_establish_dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>", None))
        self.checkBox.setText(_translate("scheme_establish_dialog", "Approve", None))
        self.label_3.setText(_translate("scheme_establish_dialog", "Various actors will receive information for further action.", None))
        self.label.setText(_translate("scheme_establish_dialog", "Scheme establishment", None))
        self.label_2.setText(_translate("scheme_establish_dialog", "This screen  contains the details of the lodgement of the scheme for approval.", None))
        self.label_5.setText(_translate("scheme_establish_dialog", "Click on Submit to complete", None))
        self.closeBtn.setText(_translate("scheme_establish_dialog", "Submit", None))

