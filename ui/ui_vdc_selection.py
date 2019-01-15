# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_vdc_selection.ui'
#
# Created: Thu Jan 10 18:09:11 2019
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

class Ui_VdcSelection(object):
    def setupUi(self, VdcSelection):
        VdcSelection.setObjectName(_fromUtf8("VdcSelection"))
        VdcSelection.resize(400, 113)
        self.verticalLayout = QtGui.QVBoxLayout(VdcSelection)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(VdcSelection)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.edtVdc = QtGui.QLineEdit(VdcSelection)
        self.edtVdc.setReadOnly(True)
        self.edtVdc.setObjectName(_fromUtf8("edtVdc"))
        self.horizontalLayout.addWidget(self.edtVdc)
        self.btnBrowse = QtGui.QPushButton(VdcSelection)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.horizontalLayout.addWidget(self.btnBrowse)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(VdcSelection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(VdcSelection)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), VdcSelection.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), VdcSelection.reject)
        QtCore.QMetaObject.connectSlotsByName(VdcSelection)

    def retranslateUi(self, VdcSelection):
        VdcSelection.setWindowTitle(_translate("VdcSelection", "VDC/Ward Selection", None))
        self.label_2.setText(_translate("VdcSelection", "VDC/Ward ", None))
        self.btnBrowse.setText(_translate("VdcSelection", "Browse ...", None))

