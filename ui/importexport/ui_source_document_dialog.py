# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_source_document_dialog.ui'
#
# Created: Wed Aug 17 09:57:35 2016
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SourceDocumentTranslatorDialog(object):
    def setupUi(self, SourceDocumentTranslatorDialog):
        SourceDocumentTranslatorDialog.setObjectName(_fromUtf8("SourceDocumentTranslatorDialog"))
        SourceDocumentTranslatorDialog.resize(497, 127)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SourceDocumentTranslatorDialog.sizePolicy().hasHeightForWidth())
        SourceDocumentTranslatorDialog.setSizePolicy(sizePolicy)
        SourceDocumentTranslatorDialog.setMinimumSize(QtCore.QSize(0, 127))
        self.gridLayout = QtGui.QGridLayout(SourceDocumentTranslatorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 3)
        self.label = QtGui.QLabel(SourceDocumentTranslatorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.txtRootFolder = QtGui.QLineEdit(SourceDocumentTranslatorDialog)
        self.txtRootFolder.setMinimumSize(QtCore.QSize(0, 30))
        self.txtRootFolder.setObjectName(_fromUtf8("txtRootFolder"))
        self.gridLayout.addWidget(self.txtRootFolder, 1, 1, 1, 1)
        self.btn_source_doc_folder = QtGui.QToolButton(SourceDocumentTranslatorDialog)
        self.btn_source_doc_folder.setMinimumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/open_file.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_source_doc_folder.setIcon(icon)
        self.btn_source_doc_folder.setObjectName(_fromUtf8("btn_source_doc_folder"))
        self.gridLayout.addWidget(self.btn_source_doc_folder, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SourceDocumentTranslatorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 3)

        self.retranslateUi(SourceDocumentTranslatorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SourceDocumentTranslatorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SourceDocumentTranslatorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SourceDocumentTranslatorDialog)

    def retranslateUi(self, SourceDocumentTranslatorDialog):
        SourceDocumentTranslatorDialog.setWindowTitle(QtGui.QApplication.translate("SourceDocumentTranslatorDialog", "Supporting Documents Translator Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SourceDocumentTranslatorDialog", "Supporting documents folder", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_source_doc_folder.setText(QtGui.QApplication.translate("SourceDocumentTranslatorDialog", "...", None, QtGui.QApplication.UnicodeUTF8))

from stdm import resources_rc