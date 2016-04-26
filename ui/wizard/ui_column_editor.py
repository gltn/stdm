# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_column_editor.ui'
#
# Created: Mon Apr 25 15:23:47 2016
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

class Ui_ColumnEditor(object):
    def setupUi(self, ColumnEditor):
        ColumnEditor.setObjectName(_fromUtf8("ColumnEditor"))
        ColumnEditor.resize(348, 302)
        self.formLayout = QtGui.QFormLayout(ColumnEditor)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_2 = QtGui.QLabel(ColumnEditor)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtColName = QtGui.QLineEdit(ColumnEditor)
        self.edtColName.setObjectName(_fromUtf8("edtColName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtColName)
        self.label_3 = QtGui.QLabel(ColumnEditor)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_3)
        self.edtColDesc = QtGui.QLineEdit(ColumnEditor)
        self.edtColDesc.setObjectName(_fromUtf8("edtColDesc"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtColDesc)
        self.label_11 = QtGui.QLabel(ColumnEditor)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_11)
        self.edtUserTip = QtGui.QLineEdit(ColumnEditor)
        self.edtUserTip.setText(_fromUtf8(""))
        self.edtUserTip.setObjectName(_fromUtf8("edtUserTip"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.edtUserTip)
        self.label_4 = QtGui.QLabel(ColumnEditor)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.cboDataType = QtGui.QComboBox(ColumnEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboDataType.sizePolicy().hasHeightForWidth())
        self.cboDataType.setSizePolicy(sizePolicy)
        self.cboDataType.setEditable(False)
        self.cboDataType.setObjectName(_fromUtf8("cboDataType"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.cboDataType)
        self.btnColProp = QtGui.QPushButton(ColumnEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnColProp.sizePolicy().hasHeightForWidth())
        self.btnColProp.setSizePolicy(sizePolicy)
        self.btnColProp.setObjectName(_fromUtf8("btnColProp"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.btnColProp)
        self.cbMandt = QtGui.QCheckBox(ColumnEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbMandt.sizePolicy().hasHeightForWidth())
        self.cbMandt.setSizePolicy(sizePolicy)
        self.cbMandt.setChecked(False)
        self.cbMandt.setObjectName(_fromUtf8("cbMandt"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.cbMandt)
        self.cbSearch = QtGui.QCheckBox(ColumnEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbSearch.sizePolicy().hasHeightForWidth())
        self.cbSearch.setSizePolicy(sizePolicy)
        self.cbSearch.setObjectName(_fromUtf8("cbSearch"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.cbSearch)
        self.cbUnique = QtGui.QCheckBox(ColumnEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbUnique.sizePolicy().hasHeightForWidth())
        self.cbUnique.setSizePolicy(sizePolicy)
        self.cbUnique.setObjectName(_fromUtf8("cbUnique"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.cbUnique)
        self.cbIndex = QtGui.QCheckBox(ColumnEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbIndex.sizePolicy().hasHeightForWidth())
        self.cbIndex.setSizePolicy(sizePolicy)
        self.cbIndex.setObjectName(_fromUtf8("cbIndex"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.cbIndex)
        self.buttonBox = QtGui.QDialogButtonBox(ColumnEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(9, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(ColumnEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ColumnEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ColumnEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(ColumnEditor)
        ColumnEditor.setTabOrder(self.edtColName, self.edtColDesc)
        ColumnEditor.setTabOrder(self.edtColDesc, self.edtUserTip)
        ColumnEditor.setTabOrder(self.edtUserTip, self.cboDataType)
        ColumnEditor.setTabOrder(self.cboDataType, self.btnColProp)
        ColumnEditor.setTabOrder(self.btnColProp, self.cbMandt)
        ColumnEditor.setTabOrder(self.cbMandt, self.cbSearch)
        ColumnEditor.setTabOrder(self.cbSearch, self.cbUnique)
        ColumnEditor.setTabOrder(self.cbUnique, self.cbIndex)
        ColumnEditor.setTabOrder(self.cbIndex, self.buttonBox)

    def retranslateUi(self, ColumnEditor):
        ColumnEditor.setWindowTitle(_translate("ColumnEditor", "Column editor", None))
        self.label_2.setText(_translate("ColumnEditor", "Column name", None))
        self.edtColName.setPlaceholderText(_translate("ColumnEditor", "Enter column name", None))
        self.label_3.setText(_translate("ColumnEditor", "Description", None))
        self.edtColDesc.setPlaceholderText(_translate("ColumnEditor", "Column Description", None))
        self.label_11.setText(_translate("ColumnEditor", "User tip", None))
        self.edtUserTip.setPlaceholderText(_translate("ColumnEditor", "Enter text to appear in the form as a tooltip", None))
        self.label_4.setText(_translate("ColumnEditor", "Column data type", None))
        self.btnColProp.setText(_translate("ColumnEditor", "Column properties ...", None))
        self.cbMandt.setText(_translate("ColumnEditor", "Is mandatory", None))
        self.cbSearch.setText(_translate("ColumnEditor", "Is searchable", None))
        self.cbUnique.setText(_translate("ColumnEditor", "Is unique", None))
        self.cbIndex.setText(_translate("ColumnEditor", "Is column Indexed", None))

