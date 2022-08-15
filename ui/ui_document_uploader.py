# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_document_uploader.ui'
#
# Created: Tue May 17 12:37:51 2022
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

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

class Ui_DocumentUploader(object):
    def setupUi(self, DocumentUploader):
        DocumentUploader.setObjectName(_fromUtf8("DocumentUploader"))
        DocumentUploader.resize(800, 442)
        self.centralwidget = QtGui.QWidget(DocumentUploader)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.lvFiles = QtGui.QListView(self.splitter)
        self.lvFiles.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.lvFiles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lvFiles.setModelColumn(0)
        self.lvFiles.setObjectName(_fromUtf8("lvFiles"))
        self.edtProgress = QtGui.QTextEdit(self.splitter)
        self.edtProgress.setObjectName(_fromUtf8("edtProgress"))
        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 3)
        self.btnFolder = QtGui.QPushButton(self.centralwidget)
        self.btnFolder.setObjectName(_fromUtf8("btnFolder"))
        self.gridLayout.addWidget(self.btnFolder, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtFolder = QtGui.QLineEdit(self.centralwidget)
        self.edtFolder.setObjectName(_fromUtf8("edtFolder"))
        self.gridLayout.addWidget(self.edtFolder, 0, 1, 1, 1)
        self.cbAll = QtGui.QCheckBox(self.centralwidget)
        self.cbAll.setObjectName(_fromUtf8("cbAll"))
        self.gridLayout.addWidget(self.cbAll, 1, 0, 1, 1)

        self.cbAllowDuplicate = QtGui.QCheckBox(self.centralwidget)
        self.cbAllowDuplicate.setObjectName(_fromUtf8("cbAllowDuplicate"))
        self.gridLayout.addWidget(self.cbAllowDuplicate, 3, 0, 1, 1)
        self.cbDelAfterUpload = QtGui.QCheckBox(self.centralwidget)
        self.cbDelAfterUpload.setObjectName(_fromUtf8("cbDelAfterUpload"))
        self.gridLayout.addWidget(self.cbDelAfterUpload, 3, 1, 1, 1)

        self.btnUpload = QtGui.QPushButton(self.centralwidget)
        self.btnUpload.setObjectName(_fromUtf8("btnUpload"))
        self.gridLayout.addWidget(self.btnUpload, 3, 2, 1, 1)
        
        self.verticalLayout.addLayout(self.gridLayout)
        DocumentUploader.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(DocumentUploader)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        DocumentUploader.setStatusBar(self.statusbar)

        self.retranslateUi(DocumentUploader)
        QtCore.QMetaObject.connectSlotsByName(DocumentUploader)

    def retranslateUi(self, DocumentUploader):
        DocumentUploader.setWindowTitle(_translate("DocumentUploader", "Scanned Document Uploader", None))
        self.btnFolder.setText(_translate("DocumentUploader", "Folder ...", None))
        self.label.setText(_translate("DocumentUploader", "Scanned Certificates Directory:", None))
        self.cbAll.setText(_translate("DocumentUploader", "All", None))
        self.btnUpload.setText(_translate("DocumentUploader", "Upload", None))
        self.cbAllowDuplicate.setText(_translate("DocumentUploader", "Allow Uploading Duplicates", None))
        self.cbAllowDuplicate.setCheckState(Qt.Checked)
        self.cbDelAfterUpload.setText(_translate("DocumentUploader", "Delete Documents After Upload", None))
