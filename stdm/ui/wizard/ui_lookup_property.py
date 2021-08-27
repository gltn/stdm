# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wizard\ui_lookup_property.ui'
#
# Created: Fri Aug 27 13:01:59 2021
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

class Ui_LookupProperty(object):
    def setupUi(self, LookupProperty):
        LookupProperty.setObjectName(_fromUtf8("LookupProperty"))
        LookupProperty.resize(436, 122)
        self.verticalLayout = QtGui.QVBoxLayout(LookupProperty)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(LookupProperty)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.cboPrimaryEntity = QtGui.QComboBox(LookupProperty)
        self.cboPrimaryEntity.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.cboPrimaryEntity.setObjectName(_fromUtf8("cboPrimaryEntity"))
        self.horizontalLayout.addWidget(self.cboPrimaryEntity)
        self.btnNewlookup = QtGui.QPushButton(LookupProperty)
        self.btnNewlookup.setObjectName(_fromUtf8("btnNewlookup"))
        self.horizontalLayout.addWidget(self.btnNewlookup)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(LookupProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(LookupProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupProperty)

    def retranslateUi(self, LookupProperty):
        LookupProperty.setWindowTitle(_translate("LookupProperty", "Lookup property", None))
        self.label.setText(_translate("LookupProperty", "Lookup", None))
        self.btnNewlookup.setText(_translate("LookupProperty", "New lookup ...", None))

