# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_multiple_enumeration_dialog.ui'
#
# Created: Fri Dec 13 13:19:56 2019
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EnumerationTranslatorDialog(object):
    def setupUi(self, EnumerationTranslatorDialog):
        EnumerationTranslatorDialog.setObjectName(_fromUtf8("EnumerationTranslatorDialog"))
        EnumerationTranslatorDialog.resize(443, 192)
        self.gridLayout_3 = QtGui.QGridLayout(EnumerationTranslatorDialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.vl_notification = QtGui.QVBoxLayout()
        self.vl_notification.setObjectName(_fromUtf8("vl_notification"))
        self.gridLayout_3.addLayout(self.vl_notification, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EnumerationTranslatorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(EnumerationTranslatorDialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)
        self.txt_source_col = QtGui.QLineEdit(self.groupBox_2)
        self.txt_source_col.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_source_col.setStyleSheet(_fromUtf8("background-color: rgb(232, 232, 232);"))
        self.txt_source_col.setReadOnly(True)
        self.txt_source_col.setObjectName(_fromUtf8("txt_source_col"))
        self.gridLayout_2.addWidget(self.txt_source_col, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)
        self.cbo_separator = QtGui.QComboBox(self.groupBox_2)
        self.cbo_separator.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_separator.setObjectName(_fromUtf8("cbo_separator"))
        self.gridLayout_2.addWidget(self.cbo_separator, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.retranslateUi(EnumerationTranslatorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EnumerationTranslatorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EnumerationTranslatorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EnumerationTranslatorDialog)

    def retranslateUi(self, EnumerationTranslatorDialog):
        EnumerationTranslatorDialog.setWindowTitle(QtGui.QApplication.translate("EnumerationTranslatorDialog", "Multiple Select Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("EnumerationTranslatorDialog", "Data Source Settings:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("EnumerationTranslatorDialog", "Source column", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("EnumerationTranslatorDialog", "Separator", None, QtGui.QApplication.UnicodeUTF8))

