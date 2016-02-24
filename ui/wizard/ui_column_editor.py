# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_column_editor.ui'
#
# Created: Tue Feb 23 16:31:24 2016
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
        ColumnEditor.resize(376, 305)
        self.buttonBox = QtGui.QDialogButtonBox(ColumnEditor)
        self.buttonBox.setGeometry(QtCore.QRect(210, 277, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.edtUserTip = QtGui.QLineEdit(ColumnEditor)
        self.edtUserTip.setGeometry(QtCore.QRect(110, 69, 261, 20))
        self.edtUserTip.setText(_fromUtf8(""))
        self.edtUserTip.setObjectName(_fromUtf8("edtUserTip"))
        self.cbUnique = QtGui.QCheckBox(ColumnEditor)
        self.cbUnique.setGeometry(QtCore.QRect(110, 218, 91, 16))
        self.cbUnique.setObjectName(_fromUtf8("cbUnique"))
        self.label_3 = QtGui.QLabel(ColumnEditor)
        self.label_3.setGeometry(QtCore.QRect(19, 41, 53, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_2 = QtGui.QLabel(ColumnEditor)
        self.label_2.setGeometry(QtCore.QRect(19, 11, 64, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_4 = QtGui.QLabel(ColumnEditor)
        self.label_4.setGeometry(QtCore.QRect(19, 98, 85, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.edtColName = QtGui.QLineEdit(ColumnEditor)
        self.edtColName.setGeometry(QtCore.QRect(110, 11, 261, 20))
        self.edtColName.setObjectName(_fromUtf8("edtColName"))
        self.edtColDesc = QtGui.QLineEdit(ColumnEditor)
        self.edtColDesc.setGeometry(QtCore.QRect(110, 39, 261, 20))
        self.edtColDesc.setObjectName(_fromUtf8("edtColDesc"))
        self.label_11 = QtGui.QLabel(ColumnEditor)
        self.label_11.setGeometry(QtCore.QRect(19, 69, 37, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.cbSearch = QtGui.QCheckBox(ColumnEditor)
        self.cbSearch.setGeometry(QtCore.QRect(110, 188, 91, 16))
        self.cbSearch.setObjectName(_fromUtf8("cbSearch"))
        self.cbIndex = QtGui.QCheckBox(ColumnEditor)
        self.cbIndex.setGeometry(QtCore.QRect(110, 248, 121, 16))
        self.cbIndex.setObjectName(_fromUtf8("cbIndex"))
        self.cboDataType = QtGui.QComboBox(ColumnEditor)
        self.cboDataType.setGeometry(QtCore.QRect(110, 98, 261, 20))
        self.cboDataType.setEditable(False)
        self.cboDataType.setObjectName(_fromUtf8("cboDataType"))
        self.btnColProp = QtGui.QPushButton(ColumnEditor)
        self.btnColProp.setGeometry(QtCore.QRect(110, 128, 261, 23))
        self.btnColProp.setObjectName(_fromUtf8("btnColProp"))
        self.cbMandt = QtGui.QCheckBox(ColumnEditor)
        self.cbMandt.setGeometry(QtCore.QRect(110, 161, 111, 16))
        self.cbMandt.setChecked(False)
        self.cbMandt.setObjectName(_fromUtf8("cbMandt"))

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
        self.edtUserTip.setPlaceholderText(_translate("ColumnEditor", "Enter text to appear in the form as a tooltip", None))
        self.cbUnique.setText(_translate("ColumnEditor", "Is unique", None))
        self.label_3.setText(_translate("ColumnEditor", "Description", None))
        self.label_2.setText(_translate("ColumnEditor", "Column name", None))
        self.label_4.setText(_translate("ColumnEditor", "Column data type", None))
        self.edtColName.setPlaceholderText(_translate("ColumnEditor", "Enter column name", None))
        self.edtColDesc.setPlaceholderText(_translate("ColumnEditor", "Column Description", None))
        self.label_11.setText(_translate("ColumnEditor", "User tip", None))
        self.cbSearch.setText(_translate("ColumnEditor", "Is searchable", None))
        self.cbIndex.setText(_translate("ColumnEditor", "Is column Indexed", None))
        self.btnColProp.setText(_translate("ColumnEditor", "Column properties ...", None))
        self.cbMandt.setText(_translate("ColumnEditor", "Is mandatory", None))

