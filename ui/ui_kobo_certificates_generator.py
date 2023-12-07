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

class Ui_KoboCertificatesGenerator(object):
    def setupUi(self, KoboCertificatesGenerator):
        KoboCertificatesGenerator.setObjectName(_fromUtf8("KoboCertificatesGenerator"))
        KoboCertificatesGenerator.resize(518, 288)
        self.verticalLayout = QtGui.QVBoxLayout(KoboCertificatesGenerator)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))

        self.gridLayout_path = QtGui.QGridLayout()
        self.gridLayout_path.setObjectName(_fromUtf8("gridLayout_path"))
        self.bt_outpath = QtGui.QPushButton(None)
        self.bt_outpath.setObjectName(_fromUtf8("bt_outpath"))
        self.gridLayout_path.addWidget(self.bt_outpath, 0, 5, 1, 1)
        self.lb_outpath = QtGui.QLabel(None)
        self.lb_outpath.setObjectName(_fromUtf8("lb_outpath"))
        self.gridLayout_path.addWidget(self.lb_outpath, 0, 0, 1, 1)
        self.ed_outpath = QtGui.QLineEdit(None)
        self.ed_outpath.setObjectName(_fromUtf8("ed_outpath"))
        self.gridLayout_path.addWidget(self.ed_outpath, 0, 1, 1, 3)
        self.verticalLayout.addLayout(self.gridLayout_path)
        
        self.edtProgress = QtGui.QTextEdit(KoboCertificatesGenerator)
        self.edtProgress.setObjectName(_fromUtf8("edtProgress"))
        self.verticalLayout.addWidget(self.edtProgress)

        self.gridLayout_options = QtGui.QGridLayout()
        self.gridLayout_options.setObjectName(_fromUtf8("gridLayout_options"))
        self.cbIgnorePrinted = QtGui.QCheckBox(None)
        self.cbIgnorePrinted.setObjectName(_fromUtf8("cbIgnorePrinted"))
        self.gridLayout_options.addWidget(self.cbIgnorePrinted, 0, 0, 1, 1)
        self.cbUploadCertificates = QtGui.QCheckBox(None)
        self.cbUploadCertificates.setObjectName(_fromUtf8("UploadCertificates"))
        self.gridLayout_options.addWidget(self.cbUploadCertificates, 0, 1, 1, 1)
        self.cbCertLang = QtGui.QCheckBox(None)
        self.cbCertLang.setObjectName(_fromUtf8("cbCertLang"))
        self.gridLayout_options.addWidget(self.cbCertLang, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_options)
        

        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblPcount = QtGui.QLabel(KoboCertificatesGenerator)
        self.lblPcount.setObjectName(_fromUtf8("lblPcount"))
        self.gridLayout.addWidget(self.lblPcount, 1, 1, 1, 1)
        self.lblUcount = QtGui.QLabel(KoboCertificatesGenerator)
        self.lblUcount.setObjectName(_fromUtf8("lblUcount"))
        self.gridLayout.addWidget(self.lblUcount, 1, 3, 1, 1)
        self.lb_uploadcaption = QtGui.QLabel(KoboCertificatesGenerator)
        self.lb_uploadcaption.setObjectName(_fromUtf8("lb_uploadcaption"))
        self.gridLayout.addWidget(self.lb_uploadcaption, 1, 2, 1, 1)
        self.lb_printcaption = QtGui.QLabel(KoboCertificatesGenerator)
        self.lb_printcaption.setObjectName(_fromUtf8("lb_printcaption"))
        self.gridLayout.addWidget(self.lb_printcaption, 1, 0, 1, 1)
        self.btnGenerate = QtGui.QPushButton(KoboCertificatesGenerator)
        self.btnGenerate.setObjectName(_fromUtf8("btnGenerate"))
        self.gridLayout.addWidget(self.btnGenerate, 1, 4, 1, 1)
        self.btnCancel = QtGui.QPushButton(KoboCertificatesGenerator)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 1, 5, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(KoboCertificatesGenerator)
        QtCore.QMetaObject.connectSlotsByName(KoboCertificatesGenerator)

    def retranslateUi(self, KoboCertificatesGenerator):
        KoboCertificatesGenerator.setWindowTitle(_translate("KoboCertificatesGenerator", "Dialog", None))
        self.lblPcount.setText(_translate("KoboCertificatesGenerator", "0", None))
        self.lblUcount.setText(_translate("KoboCertificatesGenerator", "0", None))
        self.cbIgnorePrinted.setText(_translate("KoboCertificatesGenerator", "Re-generate Existing Certificates", None))
        self.cbCertLang.setText(_translate("KoboCertificatesGenerator", "Arabic", None))
        self.cbUploadCertificates.setText(_translate("KoboCertificatesGenerator", "Upload Certificates", None))
        self.lb_uploadcaption.setText(_translate("KoboCertificatesGenerator", "Uploaded:", None))
        self.lb_printcaption.setText(_translate("KoboCertificatesGenerator", "Generated:", None))
        self.btnGenerate.setText(_translate("KoboCertificatesGenerator", "Generate", None))
        self.btnCancel.setText(_translate("KoboCertificatesGenerator", "Close", None))
        self.bt_outpath.setText(_translate("DocumentUploader", "Folder ...", None))
        self.lb_outpath.setText(_translate("DocumentUploader", "Select Output Path:", None))