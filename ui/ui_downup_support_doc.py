# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_downup_support_doc.ui'
#
# Created: Mon Jul 05 20:36:52 2021
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_SupportDocDownloader(object):
    def setupUi(self, SupportDocDownloader):
        SupportDocDownloader.setObjectName(_fromUtf8("SupportDocDownloader"))
        SupportDocDownloader.resize(518, 288)
        self.verticalLayout = QtGui.QVBoxLayout(SupportDocDownloader)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtProgress = QtGui.QTextEdit(SupportDocDownloader)
        self.edtProgress.setObjectName(_fromUtf8("edtProgress"))
        self.horizontalLayout.addWidget(self.edtProgress)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDcount = QtGui.QLabel(SupportDocDownloader)
        self.lblDcount.setObjectName(_fromUtf8("lblDcount"))
        self.gridLayout.addWidget(self.lblDcount, 1, 1, 1, 2)
        self.lblUcount = QtGui.QLabel(SupportDocDownloader)
        self.lblUcount.setObjectName(_fromUtf8("lblUcount"))
        self.gridLayout.addWidget(self.lblUcount, 2, 2, 1, 1)
        self.label_2 = QtGui.QLabel(SupportDocDownloader)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)
        self.label = QtGui.QLabel(SupportDocDownloader)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.btnDownload = QtGui.QPushButton(SupportDocDownloader)
        self.btnDownload.setObjectName(_fromUtf8("btnDownload"))
        self.gridLayout.addWidget(self.btnDownload, 3, 0, 1, 3)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(SupportDocDownloader)
        QtCore.QMetaObject.connectSlotsByName(SupportDocDownloader)

    def retranslateUi(self, SupportDocDownloader):
        SupportDocDownloader.setWindowTitle(_translate("SupportDocDownloader", "Dialog", None))
        self.lblDcount.setText(_translate("SupportDocDownloader", "TextLabel", None))
        self.lblUcount.setText(_translate("SupportDocDownloader", "TextLabel", None))
        self.label_2.setText(_translate("SupportDocDownloader", "Uploading:", None))
        self.label.setText(_translate("SupportDocDownloader", "Downloading:", None))
        self.btnDownload.setText(_translate("SupportDocDownloader", "Start download", None))

