# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_attribute_editor.ui'
#
# Created: Mon Jun 29 23:55:15 2015
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_editor(object):
    def setupUi(self, editor):
        editor.setObjectName(_fromUtf8("editor"))
        editor.resize(447, 368)
        self.gridLayout = QtGui.QGridLayout(editor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(editor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(editor)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_2.addWidget(self.label_9, 7, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 5, 0, 1, 1)
        self.txtAttrib = QtGui.QLineEdit(self.groupBox)
        self.txtAttrib.setObjectName(_fromUtf8("txtAttrib"))
        self.gridLayout_2.addWidget(self.txtAttrib, 4, 1, 1, 3)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.cboDatatype = QtGui.QComboBox(self.groupBox)
        self.cboDatatype.setEditable(False)
        self.cboDatatype.setObjectName(_fromUtf8("cboDatatype"))
        self.gridLayout_2.addWidget(self.cboDatatype, 3, 1, 1, 3)
        self.txtCol = QtGui.QLineEdit(self.groupBox)
        self.txtCol.setObjectName(_fromUtf8("txtCol"))
        self.gridLayout_2.addWidget(self.txtCol, 1, 1, 1, 3)
        self.txtColDesc = QtGui.QLineEdit(self.groupBox)
        self.txtColDesc.setObjectName(_fromUtf8("txtColDesc"))
        self.gridLayout_2.addWidget(self.txtColDesc, 2, 1, 1, 3)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.cboTabList = QtGui.QComboBox(self.groupBox)
        self.cboTabList.setObjectName(_fromUtf8("cboTabList"))
        self.gridLayout_2.addWidget(self.cboTabList, 0, 1, 1, 3)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.checkBox = QtGui.QCheckBox(self.groupBox)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout_2.addWidget(self.checkBox, 7, 1, 1, 1)
        self.cboNull = QtGui.QComboBox(self.groupBox)
        self.cboNull.setObjectName(_fromUtf8("cboNull"))
        self.gridLayout_2.addWidget(self.cboNull, 6, 1, 1, 3)
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_2.addWidget(self.label_7, 6, 0, 1, 1)
        self.chkPrimaryKey = QtGui.QCheckBox(self.groupBox)
        self.chkPrimaryKey.setObjectName(_fromUtf8("chkPrimaryKey"))
        self.gridLayout_2.addWidget(self.chkPrimaryKey, 5, 1, 1, 1)
        self.btnTableList = QtGui.QPushButton(self.groupBox)
        self.btnTableList.setMaximumSize(QtCore.QSize(50, 16777215))
        self.btnTableList.setObjectName(_fromUtf8("btnTableList"))
        self.gridLayout_2.addWidget(self.btnTableList, 7, 2, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 8, 0, 1, 1)
        self.label_10 = QtGui.QLabel(self.groupBox)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_2.addWidget(self.label_10, 9, 0, 1, 1)
        self.txtDefault = QtGui.QLineEdit(self.groupBox)
        self.txtDefault.setText(_fromUtf8(""))
        self.txtDefault.setObjectName(_fromUtf8("txtDefault"))
        self.gridLayout_2.addWidget(self.txtDefault, 8, 1, 1, 3)
        self.cboSearchable = QtGui.QComboBox(self.groupBox)
        self.cboSearchable.setObjectName(_fromUtf8("cboSearchable"))
        self.gridLayout_2.addWidget(self.cboSearchable, 9, 1, 1, 3)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(editor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), editor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), editor.reject)
        QtCore.QMetaObject.connectSlotsByName(editor)

    def retranslateUi(self, editor):
        editor.setWindowTitle(_translate("editor", "Table Attributes", None))
        self.groupBox.setTitle(_translate("editor", "Add Table Column", None))
        self.label_9.setText(_translate("editor", "Field is a List (Choice list)", None))
        self.label.setText(_translate("editor", "Table", None))
        self.label_6.setText(_translate("editor", "Auto Increment (Primary Key)", None))
        self.txtAttrib.setPlaceholderText(_translate("editor", "default attribute length", None))
        self.label_5.setText(_translate("editor", "Character Length", None))
        self.label_4.setText(_translate("editor", "Column Data Type", None))
        self.txtCol.setPlaceholderText(_translate("editor", "Enter column name", None))
        self.txtColDesc.setPlaceholderText(_translate("editor", "Column Description", None))
        self.label_3.setText(_translate("editor", "Description", None))
        self.label_2.setText(_translate("editor", "Column Name", None))
        self.checkBox.setText(_translate("editor", "Yes       E.g Gender (Male/Female)", None))
        self.label_7.setText(_translate("editor", "Is Mandatory Field ", None))
        self.chkPrimaryKey.setText(_translate("editor", "Yes", None))
        self.btnTableList.setText(_translate("editor", "Source", None))
        self.label_8.setText(_translate("editor", "Default Value", None))
        self.label_10.setText(_translate("editor", "Is Searchable Field", None))
        self.txtDefault.setPlaceholderText(_translate("editor", "Default value will be provided if user does not specify", None))

