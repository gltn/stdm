# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_table_property.ui'
#
# Created: Thu Jun 18 16:23:52 2015
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

class Ui_TableProperty(object):
    def setupUi(self, TableProperty):
        TableProperty.setObjectName(_fromUtf8("TableProperty"))
        TableProperty.resize(400, 520)
        self.gridLayout_3 = QtGui.QGridLayout(TableProperty)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gpRelation = QtGui.QGroupBox(TableProperty)
        self.gpRelation.setObjectName(_fromUtf8("gpRelation"))
        self.gridLayout = QtGui.QGridLayout(self.gpRelation)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.gpRelation)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.gpRelation)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 6, 0, 1, 1)
        self.cboDelAct = QtGui.QComboBox(self.gpRelation)
        self.cboDelAct.setObjectName(_fromUtf8("cboDelAct"))
        self.gridLayout.addWidget(self.cboDelAct, 5, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.gpRelation)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.cboTable = QtGui.QComboBox(self.gpRelation)
        self.cboTable.setObjectName(_fromUtf8("cboTable"))
        self.gridLayout.addWidget(self.cboTable, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.gpRelation)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.gpRelation)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.cboUpAct = QtGui.QComboBox(self.gpRelation)
        self.cboUpAct.setObjectName(_fromUtf8("cboUpAct"))
        self.gridLayout.addWidget(self.cboUpAct, 6, 1, 1, 1)
        self.cboColumn = QtGui.QComboBox(self.gpRelation)
        self.cboColumn.setObjectName(_fromUtf8("cboColumn"))
        self.gridLayout.addWidget(self.cboColumn, 4, 1, 1, 1)
        self.txtName = QtGui.QLineEdit(self.gpRelation)
        self.txtName.setObjectName(_fromUtf8("txtName"))
        self.gridLayout.addWidget(self.txtName, 0, 1, 1, 1)
        self.cboRefCol = QtGui.QComboBox(self.gpRelation)
        self.cboRefCol.setObjectName(_fromUtf8("cboRefCol"))
        self.gridLayout.addWidget(self.cboRefCol, 1, 1, 1, 1)
        self.label_11 = QtGui.QLabel(self.gpRelation)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout.addWidget(self.label_11, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gpRelation, 0, 0, 2, 2)
        self.gpConstraint = QtGui.QGroupBox(TableProperty)
        self.gpConstraint.setObjectName(_fromUtf8("gpConstraint"))
        self.gridLayout_5 = QtGui.QGridLayout(self.gpConstraint)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_6 = QtGui.QLabel(self.gpConstraint)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_5.addWidget(self.label_6, 0, 0, 1, 1)
        self.cboType = QtGui.QComboBox(self.gpConstraint)
        self.cboType.setObjectName(_fromUtf8("cboType"))
        self.gridLayout_5.addWidget(self.cboType, 0, 1, 1, 1)
        self.txtType = QtGui.QLineEdit(self.gpConstraint)
        self.txtType.setObjectName(_fromUtf8("txtType"))
        self.gridLayout_5.addWidget(self.txtType, 1, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.gpConstraint)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_5.addWidget(self.label_7, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gpConstraint, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(TableProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 4, 0, 1, 1)

        self.retranslateUi(TableProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TableProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TableProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(TableProperty)

    def retranslateUi(self, TableProperty):
        TableProperty.setWindowTitle(_translate("TableProperty", "Table Properties", None))
        self.gpRelation.setTitle(_translate("TableProperty", "Add relation from parent table", None))
        self.label.setText(_translate("TableProperty", "Relation name", None))
        self.label_5.setText(_translate("TableProperty", "On Update action", None))
        self.label_4.setText(_translate("TableProperty", "On Delete action", None))
        self.label_2.setText(_translate("TableProperty", "Reference table", None))
        self.label_3.setText(_translate("TableProperty", "Referenced column", None))
        self.label_11.setText(_translate("TableProperty", "Local Column", None))
        self.gpConstraint.setTitle(_translate("TableProperty", "Column information to dispay when browsing for foreign key", None))
        self.label_6.setText(_translate("TableProperty", "Display Column", None))
        self.label_7.setText(_translate("TableProperty", "Comments", None))

