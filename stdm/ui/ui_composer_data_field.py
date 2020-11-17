# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_data_field.ui'
#
# Created: Sat May 17 05:01:36 2014
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


class Ui_frmComposerFieldEditor(object):
    def setupUi(self, frmComposerFieldEditor):
        frmComposerFieldEditor.setObjectName(_fromUtf8("frmComposerFieldEditor"))
        frmComposerFieldEditor.resize(281, 76)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmComposerFieldEditor.sizePolicy().hasHeightForWidth())
        frmComposerFieldEditor.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(frmComposerFieldEditor)
        self.gridLayout.setVerticalSpacing(11)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cboDataField = QtGui.QComboBox(frmComposerFieldEditor)
        self.cboDataField.setMinimumSize(QtCore.QSize(0, 30))
        self.cboDataField.setObjectName(_fromUtf8("cboDataField"))
        self.gridLayout.addWidget(self.cboDataField, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(frmComposerFieldEditor)
        self.label_2.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(frmComposerFieldEditor)
        self.label.setStyleSheet(_fromUtf8("padding: 2px; font-weight: bold; background-color: rgb(200, 200, 200);"))
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.retranslateUi(frmComposerFieldEditor)
        QtCore.QMetaObject.connectSlotsByName(frmComposerFieldEditor)

    def retranslateUi(self, frmComposerFieldEditor):
        frmComposerFieldEditor.setWindowTitle(_translate("frmComposerFieldEditor", "Table Column Editor", None))
        self.label_2.setText(_translate("frmComposerFieldEditor", "Data Field", None))
        self.label.setText(_translate("frmComposerFieldEditor", "Field", None))
