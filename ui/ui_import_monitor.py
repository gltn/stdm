# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_import_monitor.ui'
#
# Created: Sun July 30 18:37:51 2022
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

class Ui_ImportMonitor(object):
    def setupUi(self, ImportMonitor):
        ImportMonitor.setObjectName(_fromUtf8("ImportMonitor"))
        ImportMonitor.resize(800, 442)
        self.centralwidget = QtGui.QWidget(ImportMonitor)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.lvSessions = QtGui.QListView(self.splitter)
        self.lvSessions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.lvSessions.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lvSessions.setModelColumn(0)
        self.lvSessions.setObjectName(_fromUtf8("lvSessions"))
        self.edtProgress = QtGui.QTextEdit(self.splitter)
        self.edtProgress.setObjectName(_fromUtf8("edtProgress"))
        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 3)
        
        self.verticalLayout.addLayout(self.gridLayout)
        ImportMonitor.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(ImportMonitor)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        ImportMonitor.setStatusBar(self.statusbar)

        self.retranslateUi(ImportMonitor)
        QtCore.QMetaObject.connectSlotsByName(ImportMonitor)

    def retranslateUi(self, ImportMonitor):
        ImportMonitor.setWindowTitle(_translate("ImportMonitor", "Scanned Document Uploader", None))
