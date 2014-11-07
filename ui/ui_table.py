# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_table.ui'
#
# Created: Fri May  2 13:07:13 2014
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

class Ui_table(object):
    def setupUi(self, table):
        table.setObjectName(_fromUtf8("table"))
        table.resize(400, 211)
        self.gridLayout_2 = QtGui.QGridLayout(table)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(table)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.txtTable = QtGui.QLineEdit(self.groupBox)
        self.txtTable.setObjectName(_fromUtf8("txtTable"))
        self.gridLayout.addWidget(self.txtTable, 0, 1, 1, 1)
        self.frame = QtGui.QFrame(self.groupBox)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_3 = QtGui.QGridLayout(self.frame)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.widget = QtGui.QWidget(self.frame)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout_4 = QtGui.QGridLayout(self.widget)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.cboInheritTable = QtGui.QComboBox(self.widget)
        self.cboInheritTable.setObjectName(_fromUtf8("cboInheritTable"))
        self.gridLayout_4.addWidget(self.cboInheritTable, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.widget, 2, 0, 1, 2)
        self.checkBox = QtGui.QCheckBox(self.frame)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout_3.addWidget(self.checkBox, 1, 0, 1, 2)
        self.chkDefault = QtGui.QCheckBox(self.frame)
        self.chkDefault.setObjectName(_fromUtf8("chkDefault"))
        self.gridLayout_3.addWidget(self.chkDefault, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 2, 0, 1, 2)
        self.txtDesc = QtGui.QLineEdit(self.groupBox)
        self.txtDesc.setMinimumSize(QtCore.QSize(120, 0))
        self.txtDesc.setObjectName(_fromUtf8("txtDesc"))
        self.gridLayout.addWidget(self.txtDesc, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(table)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(table)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), table.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), table.reject)
        QtCore.QMetaObject.connectSlotsByName(table)

    def retranslateUi(self, table):
        table.setWindowTitle(_translate("table", "Dialog", None))
        self.groupBox.setTitle(_translate("table", "Table Editor", None))
        self.label.setText(_translate("table", "Table Name", None))
        self.txtTable.setPlaceholderText(_translate("table", "Table name", None))
        self.label_3.setText(_translate("table", "Inherits from ", None))
        self.checkBox.setText(_translate("table", "Inherit columns from another table", None))
        self.chkDefault.setText(_translate("table", "Auto create default column with primary key", None))
        self.txtDesc.setPlaceholderText(_translate("table", "Table description", None))
        self.label_2.setText(_translate("table", "Description", None))

