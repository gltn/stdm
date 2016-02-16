# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_entity.ui'
#
# Created: Sun Jan 24 12:40:21 2016
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

class Ui_dlgEntity(object):
    def setupUi(self, dlgEntity):
        dlgEntity.setObjectName(_fromUtf8("dlgEntity"))
        dlgEntity.resize(400, 197)
        self.gridLayout_2 = QtGui.QGridLayout(dlgEntity)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(dlgEntity)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtDesc = QtGui.QLineEdit(self.groupBox)
        self.txtDesc.setMinimumSize(QtCore.QSize(120, 0))
        self.txtDesc.setObjectName(_fromUtf8("txtDesc"))
        self.gridLayout.addWidget(self.txtDesc, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtTable = QtGui.QLineEdit(self.groupBox)
        self.txtTable.setObjectName(_fromUtf8("txtTable"))
        self.gridLayout.addWidget(self.txtTable, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(dlgEntity)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(dlgEntity)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgEntity.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgEntity.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgEntity)

    def retranslateUi(self, dlgEntity):
        dlgEntity.setWindowTitle(_translate("dlgEntity", "Dialog", None))
        self.groupBox.setTitle(_translate("dlgEntity", "Entity Editor", None))
        self.txtDesc.setPlaceholderText(_translate("dlgEntity", "Table description", None))
        self.label_2.setText(_translate("dlgEntity", "Description", None))
        self.txtTable.setPlaceholderText(_translate("dlgEntity", "Table name", None))
        self.label.setText(_translate("dlgEntity", "Entity Name", None))

