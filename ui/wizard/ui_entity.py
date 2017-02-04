# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_entity.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(dlgEntity)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.edtTable = QtGui.QLineEdit(dlgEntity)
        self.edtTable.setObjectName(_fromUtf8("edtTable"))
        self.horizontalLayout.addWidget(self.edtTable)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(dlgEntity)
        self.label_2.setMaximumSize(QtCore.QSize(101, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.edtDesc = QtGui.QLineEdit(dlgEntity)
        self.edtDesc.setMinimumSize(QtCore.QSize(120, 0))
        self.edtDesc.setObjectName(_fromUtf8("edtDesc"))
        self.horizontalLayout_2.addWidget(self.edtDesc)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
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
        self.label.setText(_translate("dlgEntity", "Entity Name", None))
        self.edtTable.setPlaceholderText(_translate("dlgEntity", "Table name", None))
        self.label_2.setText(_translate("dlgEntity", "Description", None))
        self.edtDesc.setPlaceholderText(_translate("dlgEntity", "Table description", None))
        self.cbSupportDoc.setText(_translate("dlgEntity", "Allow supporting documents?", None))

