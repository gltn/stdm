# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_entity.ui'
#
# Created: Sun Mar 12 17:13:13 2017
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
        dlgEntity.resize(307, 184)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dlgEntity.sizePolicy().hasHeightForWidth())
        dlgEntity.setSizePolicy(sizePolicy)
        dlgEntity.setMaximumSize(QtCore.QSize(500, 16777215))
        self.verticalLayout = QtGui.QVBoxLayout(dlgEntity)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.notif_bar = QtGui.QVBoxLayout()
        self.notif_bar.setObjectName(_fromUtf8("notif_bar"))
        self.verticalLayout.addLayout(self.notif_bar)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtDesc = QtGui.QLineEdit(dlgEntity)
        self.edtDesc.setMinimumSize(QtCore.QSize(0, 0))
        self.edtDesc.setObjectName(_fromUtf8("edtDesc"))
        self.gridLayout.addWidget(self.edtDesc, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(dlgEntity)
        self.label_2.setMinimumSize(QtCore.QSize(68, 0))
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(dlgEntity)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtTable = QtGui.QLineEdit(dlgEntity)
        self.edtTable.setObjectName(_fromUtf8("edtTable"))
        self.gridLayout.addWidget(self.edtTable, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.cbSupportDoc = QtGui.QCheckBox(dlgEntity)
        self.cbSupportDoc.setObjectName(_fromUtf8("cbSupportDoc"))
        self.verticalLayout.addWidget(self.cbSupportDoc)
        self.buttonBox = QtGui.QDialogButtonBox(dlgEntity)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dlgEntity)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgEntity.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgEntity.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgEntity)

    def retranslateUi(self, dlgEntity):
        dlgEntity.setWindowTitle(_translate("dlgEntity", "Entity editor", None))
        self.edtDesc.setPlaceholderText(_translate("dlgEntity", "Table description", None))
        self.label_2.setText(_translate("dlgEntity", "Description", None))
        self.label.setText(_translate("dlgEntity", "Entity Name", None))
        self.edtTable.setPlaceholderText(_translate("dlgEntity", "Table name", None))
        self.cbSupportDoc.setText(_translate("dlgEntity", "Allow supporting documents?", None))

