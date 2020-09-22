# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_value.ui'
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

class Ui_LookupValue(object):
    def setupUi(self, LookupValue):
        LookupValue.setObjectName(_fromUtf8("LookupValue"))
        LookupValue.resize(282, 155)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LookupValue.sizePolicy().hasHeightForWidth())
        LookupValue.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(LookupValue)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.notif_bar = QtGui.QVBoxLayout()
        self.notif_bar.setObjectName(_fromUtf8("notif_bar"))
        self.verticalLayout_2.addLayout(self.notif_bar)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(LookupValue)
        self.label.setMinimumSize(QtCore.QSize(60, 0))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtValue = QtGui.QLineEdit(LookupValue)
        self.edtValue.setObjectName(_fromUtf8("edtValue"))
        self.gridLayout.addWidget(self.edtValue, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(LookupValue)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(LookupValue)
        self.edtCode.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(LookupValue)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(LookupValue)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupValue.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupValue.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupValue)
        LookupValue.setTabOrder(self.edtValue, self.buttonBox)

    def retranslateUi(self, LookupValue):
        LookupValue.setWindowTitle(_translate("LookupValue", "Lookup value", None))
        self.label.setText(_translate("LookupValue", "Value Name", None))
        self.edtValue.setPlaceholderText(_translate("LookupValue", "Enter lookup value", None))
        self.label_2.setText(_translate("LookupValue", "Code", None))

