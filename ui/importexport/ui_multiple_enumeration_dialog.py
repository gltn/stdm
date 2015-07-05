# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_multiple_enumeration_dialog.ui'
#
# Created: Tue Nov 11 15:42:50 2014
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

class Ui_EnumerationTranslatorDialog(object):
    def setupUi(self, EnumerationTranslatorDialog):
        EnumerationTranslatorDialog.setObjectName(_fromUtf8("EnumerationTranslatorDialog"))
        EnumerationTranslatorDialog.resize(372, 358)
        self.gridLayout_3 = QtGui.QGridLayout(EnumerationTranslatorDialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.vl_notification = QtGui.QVBoxLayout()
        self.vl_notification.setObjectName(_fromUtf8("vl_notification"))
        self.gridLayout_3.addLayout(self.vl_notification, 0, 0, 1, 1)
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
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)
        self.cbo_src_other_col = QtGui.QComboBox(self.groupBox_2)
        self.cbo_src_other_col.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_src_other_col.setObjectName(_fromUtf8("cbo_src_other_col"))
        self.gridLayout_2.addWidget(self.cbo_src_other_col, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)
        self.cbo_separator = QtGui.QComboBox(self.groupBox_2)
        self.cbo_separator.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_separator.setObjectName(_fromUtf8("cbo_separator"))
        self.gridLayout_2.addWidget(self.cbo_separator, 2, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(EnumerationTranslatorDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cbo_enum_table = QtGui.QComboBox(self.groupBox)
        self.cbo_enum_table.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_enum_table.setObjectName(_fromUtf8("cbo_enum_table"))
        self.gridLayout.addWidget(self.cbo_enum_table, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(120, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cbo_primary_col = QtGui.QComboBox(self.groupBox)
        self.cbo_primary_col.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_primary_col.setObjectName(_fromUtf8("cbo_primary_col"))
        self.gridLayout.addWidget(self.cbo_primary_col, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.cbo_other_col = QtGui.QComboBox(self.groupBox)
        self.cbo_other_col.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_other_col.setObjectName(_fromUtf8("cbo_other_col"))
        self.gridLayout.addWidget(self.cbo_other_col, 2, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EnumerationTranslatorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 3, 0, 1, 1)

        self.retranslateUi(EnumerationTranslatorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EnumerationTranslatorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EnumerationTranslatorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EnumerationTranslatorDialog)

    def retranslateUi(self, EnumerationTranslatorDialog):
        EnumerationTranslatorDialog.setWindowTitle(_translate("EnumerationTranslatorDialog", "Multiple Enumeration Translator Configuration", None))
        self.groupBox_2.setTitle(_translate("EnumerationTranslatorDialog", "Source Table Settings:", None))
        self.label_4.setText(_translate("EnumerationTranslatorDialog", "Source column", None))
        self.label_5.setText(_translate("EnumerationTranslatorDialog", "\'Other\' column", None))
        self.label_6.setText(_translate("EnumerationTranslatorDialog", "Separator", None))
        self.groupBox.setTitle(_translate("EnumerationTranslatorDialog", "Enumeration Table Settings:", None))
        self.label.setText(_translate("EnumerationTranslatorDialog", "Table", None))
        self.label_2.setText(_translate("EnumerationTranslatorDialog", "Primary column", None))
        self.label_3.setText(_translate("EnumerationTranslatorDialog", "\'Other\' column", None))

