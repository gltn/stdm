# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_related_table_dialog.ui'
#
# Created: Mon Nov 10 16:07:49 2014
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

class Ui_RelatedTableTranslatorDialog(object):
    def setupUi(self, RelatedTableTranslatorDialog):
        RelatedTableTranslatorDialog.setObjectName(_fromUtf8("RelatedTableTranslatorDialog"))
        RelatedTableTranslatorDialog.resize(384, 458)
        self.gridLayout_3 = QtGui.QGridLayout(RelatedTableTranslatorDialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.buttonBox = QtGui.QDialogButtonBox(RelatedTableTranslatorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(RelatedTableTranslatorDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.txt_table_name = QtGui.QLineEdit(self.groupBox)
        self.txt_table_name.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_table_name.setStyleSheet(_fromUtf8("background-color: rgb(232, 232, 232);"))
        self.txt_table_name.setReadOnly(True)
        self.txt_table_name.setObjectName(_fromUtf8("txt_table_name"))
        self.gridLayout.addWidget(self.txt_table_name, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txt_column_name = QtGui.QLineEdit(self.groupBox)
        self.txt_column_name.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_column_name.setStyleSheet(_fromUtf8("background-color: rgb(232, 232, 232);"))
        self.txt_column_name.setReadOnly(True)
        self.txt_column_name.setObjectName(_fromUtf8("txt_column_name"))
        self.gridLayout.addWidget(self.txt_column_name, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 1, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(RelatedTableTranslatorDialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.cbo_source_tables = QtGui.QComboBox(self.groupBox_2)
        self.cbo_source_tables.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_source_tables.setObjectName(_fromUtf8("cbo_source_tables"))
        self.gridLayout_2.addWidget(self.cbo_source_tables, 0, 1, 1, 1)
        self.tb_source_trans_cols = ListPairTableView(self.groupBox_2)
        self.tb_source_trans_cols.setProperty("showDropIndicator", False)
        self.tb_source_trans_cols.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tb_source_trans_cols.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tb_source_trans_cols.setObjectName(_fromUtf8("tb_source_trans_cols"))
        self.gridLayout_2.addWidget(self.tb_source_trans_cols, 2, 0, 1, 2)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.cbo_output_column = QtGui.QComboBox(self.groupBox_2)
        self.cbo_output_column.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_output_column.setObjectName(_fromUtf8("cbo_output_column"))
        self.gridLayout_2.addWidget(self.cbo_output_column, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 2, 0, 1, 1)
        self.vl_notification = QtGui.QVBoxLayout()
        self.vl_notification.setObjectName(_fromUtf8("vl_notification"))
        self.gridLayout_3.addLayout(self.vl_notification, 0, 0, 1, 1)

        self.retranslateUi(RelatedTableTranslatorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RelatedTableTranslatorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RelatedTableTranslatorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RelatedTableTranslatorDialog)

    def retranslateUi(self, RelatedTableTranslatorDialog):
        RelatedTableTranslatorDialog.setWindowTitle(_translate("RelatedTableTranslatorDialog", "Related Table Translator Configuration", None))
        self.groupBox.setTitle(_translate("RelatedTableTranslatorDialog", "Destination Table Settings:", None))
        self.label.setText(_translate("RelatedTableTranslatorDialog", "Table name", None))
        self.label_2.setText(_translate("RelatedTableTranslatorDialog", "Column name", None))
        self.groupBox_2.setTitle(_translate("RelatedTableTranslatorDialog", "Referenced Table Settings:", None))
        self.label_3.setText(_translate("RelatedTableTranslatorDialog", "Table name", None))
        self.label_4.setText(_translate("RelatedTableTranslatorDialog", "Output column", None))

from ..customcontrols import ListPairTableView
