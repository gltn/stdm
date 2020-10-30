# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_property.ui'
#
# Created: Thu Jul 21 11:58:24 2016
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
        LookupProperty.resize(337, 86)
        self.formLayout = QtGui.QFormLayout(LookupProperty)
        self.formLayout.setVerticalSpacing(18)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.splitter = QtGui.QSplitter(LookupProperty)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.label = QtGui.QLabel(self.splitter)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.cboPrimaryEntity = QtGui.QComboBox(self.splitter)
        self.cboPrimaryEntity.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.cboPrimaryEntity.setObjectName(_fromUtf8("cboPrimaryEntity"))
        self.btnNewlookup = QtGui.QPushButton(self.splitter)
        self.btnNewlookup.setObjectName(_fromUtf8("btnNewlookup"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.splitter)
        self.buttonBox = QtGui.QDialogButtonBox(LookupProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(LookupProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupProperty)

    def retranslateUi(self, LookupProperty):
        LookupProperty.setWindowTitle(_translate("LookupProperty", "Lookup property", None))
        self.label.setText(_translate("LookupProperty", "Lookup", None))
        self.btnNewlookup.setText(_translate("LookupProperty", "New lookup ...", None))

