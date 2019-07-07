# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_scheme_revision.ui'
#
# Created: Sat Jul  6 21:37:05 2019
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

class Ui_revision_Wzd(object):
    def setupUi(self, revision_Wzd):
        revision_Wzd.setObjectName(_fromUtf8("revision_Wzd"))
        revision_Wzd.resize(627, 415)
        self.wizardPage1 = QtGui.QWizardPage()
        self.wizardPage1.setObjectName(_fromUtf8("wizardPage1"))
        self.gridLayout = QtGui.QGridLayout(self.wizardPage1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.title_frame_2 = QtGui.QFrame(self.wizardPage1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.title_frame_2.sizePolicy().hasHeightForWidth())
        self.title_frame_2.setSizePolicy(sizePolicy)
        self.title_frame_2.setMinimumSize(QtCore.QSize(0, 40))
        self.title_frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.title_frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.title_frame_2.setObjectName(_fromUtf8("title_frame_2"))
        self.title_label_2 = QtGui.QLabel(self.title_frame_2)
        self.title_label_2.setGeometry(QtCore.QRect(10, 0, 141, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.title_label_2.setFont(font)
        self.title_label_2.setObjectName(_fromUtf8("title_label_2"))
        self.subtitle_label_2 = QtGui.QLabel(self.title_frame_2)
        self.subtitle_label_2.setGeometry(QtCore.QRect(10, 20, 331, 16))
        self.subtitle_label_2.setObjectName(_fromUtf8("subtitle_label_2"))
        self.gridLayout.addWidget(self.title_frame_2, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.wizardPage1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scrollArea = QtGui.QScrollArea(self.groupBox)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 587, 69))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        revision_Wzd.addPage(self.wizardPage1)
        self.wizardPage2 = QtGui.QWizardPage()
        self.wizardPage2.setObjectName(_fromUtf8("wizardPage2"))
        revision_Wzd.addPage(self.wizardPage2)

        self.retranslateUi(revision_Wzd)
        QtCore.QMetaObject.connectSlotsByName(revision_Wzd)

    def retranslateUi(self, revision_Wzd):
        revision_Wzd.setWindowTitle(_translate("revision_Wzd", "Revision", None))
        self.title_label_2.setText(_translate("revision_Wzd", "Error Details", None))
        self.subtitle_label_2.setText(_translate("revision_Wzd", "This window shows details to be revised.", None))
        self.groupBox.setTitle(_translate("revision_Wzd", "Error", None))

