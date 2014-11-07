# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_source.ui'
#
# Created: Sat May 24 21:46:00 2014
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

class Ui_Lookup(object):
    def setupUi(self, Lookup):
        Lookup.setObjectName(_fromUtf8("Lookup"))
        Lookup.resize(400, 296)
        self.gridLayout = QtGui.QGridLayout(Lookup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Lookup)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cboTable = QtGui.QComboBox(Lookup)
        self.cboTable.setObjectName(_fromUtf8("cboTable"))
        self.gridLayout.addWidget(self.cboTable, 0, 1, 1, 1)
        self.btnNew = QtGui.QPushButton(Lookup)
        self.btnNew.setObjectName(_fromUtf8("btnNew"))
        self.gridLayout.addWidget(self.btnNew, 0, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Lookup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(Lookup)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lstData = QtGui.QListWidget(self.groupBox)
        self.lstData.setObjectName(_fromUtf8("lstData"))
        self.gridLayout_2.addWidget(self.lstData, 0, 0, 1, 1)
        self.btnChoice = QtGui.QPushButton(self.groupBox)
        self.btnChoice.setObjectName(_fromUtf8("btnChoice"))
        self.gridLayout_2.addWidget(self.btnChoice, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 3)

        self.retranslateUi(Lookup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Lookup.acceptDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Lookup.reject)
        QtCore.QMetaObject.connectSlotsByName(Lookup)

    def retranslateUi(self, Lookup):
        Lookup.setWindowTitle(_translate("Lookup", "Lookup Source", None))
        self.label.setText(_translate("Lookup", "Select Lookup Table", None))
        self.btnNew.setText(_translate("Lookup", "New", None))
        self.groupBox.setTitle(_translate("Lookup", "Lookup Table Choices", None))
        self.btnChoice.setText(_translate("Lookup", "Add New Choice", None))

