# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_entity.ui'
#
# Created: Wed Aug 14 12:49:50 2024
#      by: PyQt4 UI code generator 4.10
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

class Ui_dlgLookup(object):
    def setupUi(self, dlgLookup):
        dlgLookup.setObjectName(_fromUtf8("dlgLookup"))
        dlgLookup.resize(368, 139)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dlgLookup.sizePolicy().hasHeightForWidth())
        dlgLookup.setSizePolicy(sizePolicy)
        dlgLookup.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout_2 = QtGui.QVBoxLayout(dlgLookup)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.notif_bar = QtGui.QVBoxLayout()
        self.notif_bar.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.notif_bar.setObjectName(_fromUtf8("notif_bar"))
        self.verticalLayout_2.addLayout(self.notif_bar)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(dlgLookup)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(dlgLookup)
        self.edtName.setMinimumSize(QtCore.QSize(0, 22))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(dlgLookup)
        self.label_2.setMaximumSize(QtCore.QSize(777, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)
        self.label_3 = QtGui.QLabel(dlgLookup)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.edtValueMaxLen = QtGui.QSpinBox(dlgLookup)
        self.edtValueMaxLen.setMinimum(50)
        self.edtValueMaxLen.setMaximum(999)
        self.edtValueMaxLen.setObjectName(_fromUtf8("edtValueMaxLen"))
        self.gridLayout.addWidget(self.edtValueMaxLen, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(dlgLookup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(dlgLookup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgLookup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgLookup.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgLookup)

    def retranslateUi(self, dlgLookup):
        dlgLookup.setWindowTitle(_translate("dlgLookup", "Lookup entity", None))
        self.label.setText(_translate("dlgLookup", "Lookup Name", None))
        self.edtName.setPlaceholderText(_translate("dlgLookup", "Enter lookup name", None))
        self.label_2.setText(_translate("dlgLookup", "`check_` prefix will be appended on the lookup name", None))
        self.label_3.setText(_translate("dlgLookup", "Value Max Len", None))

