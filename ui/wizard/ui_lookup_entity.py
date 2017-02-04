# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_entity.ui'
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

class Ui_dlgLookup(object):
    def setupUi(self, dlgLookup):
        dlgLookup.setObjectName(_fromUtf8("dlgLookup"))
        dlgLookup.resize(389, 164)
        dlgLookup.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout_2 = QtGui.QVBoxLayout(dlgLookup)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.notif_bar = QtGui.QVBoxLayout()
        self.notif_bar.setObjectName(_fromUtf8("notif_bar"))
        self.verticalLayout_2.addLayout(self.notif_bar)
        self.label_2 = QtGui.QLabel(dlgLookup)
        self.label_2.setMaximumSize(QtCore.QSize(777, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(dlgLookup)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.edtName = QtGui.QLineEdit(dlgLookup)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.horizontalLayout.addWidget(self.edtName)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
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
        self.label_2.setText(_translate("dlgLookup", "`check_` prefix will be appended on the lookup name", None))
        self.label.setText(_translate("dlgLookup", "Lookup Name", None))
        self.edtName.setPlaceholderText(_translate("dlgLookup", "Enter lookup name", None))

