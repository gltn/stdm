# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_doc_selector.ui'
#
# Created: Sat May 24 10:34:54 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_frmDocumentSelector(object):
    def setupUi(self, frmDocumentSelector):
        frmDocumentSelector.setObjectName(_fromUtf8("frmDocumentSelector"))
        frmDocumentSelector.resize(323, 234)
        self.gridLayout = QtGui.QGridLayout(frmDocumentSelector)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lstDocs = QtGui.QListView(frmDocumentSelector)
        self.lstDocs.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstDocs.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstDocs.setObjectName(_fromUtf8("lstDocs"))
        self.gridLayout.addWidget(self.lstDocs, 2, 0, 1, 1)
        self.label = QtGui.QLabel(frmDocumentSelector)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.manageButtonBox = QtGui.QDialogButtonBox(frmDocumentSelector)
        self.manageButtonBox.setOrientation(QtCore.Qt.Vertical)
        self.manageButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Save)
        self.manageButtonBox.setObjectName(_fromUtf8("manageButtonBox"))
        self.gridLayout.addWidget(self.manageButtonBox, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmDocumentSelector)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)

        self.retranslateUi(frmDocumentSelector)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmDocumentSelector.reject)
        QtCore.QObject.connect(self.manageButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmDocumentSelector.reject)
        QtCore.QMetaObject.connectSlotsByName(frmDocumentSelector)

    def retranslateUi(self, frmDocumentSelector):
        frmDocumentSelector.setWindowTitle(_translate("frmDocumentSelector", "Template Selector", None))
        self.label.setText(_translate("frmDocumentSelector", "Select a document template from the list below", None))

