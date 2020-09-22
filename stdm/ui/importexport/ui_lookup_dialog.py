# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_dialog.ui'
#
# Created: Mon Jan 16 16:49:13 2017
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LookupTranslatorDialog(object):
    def setupUi(self, LookupTranslatorDialog):
        LookupTranslatorDialog.setObjectName(_fromUtf8("LookupTranslatorDialog"))
        LookupTranslatorDialog.resize(325, 163)
        self.gridLayout = QtGui.QGridLayout(LookupTranslatorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(LookupTranslatorDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(LookupTranslatorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.cbo_default = QtGui.QComboBox(LookupTranslatorDialog)
        self.cbo_default.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_default.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cbo_default.setObjectName(_fromUtf8("cbo_default"))
        self.gridLayout.addWidget(self.cbo_default, 2, 1, 1, 1)
        self.cbo_lookup = QtGui.QComboBox(LookupTranslatorDialog)
        self.cbo_lookup.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_lookup.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cbo_lookup.setObjectName(_fromUtf8("cbo_lookup"))
        self.gridLayout.addWidget(self.cbo_lookup, 1, 1, 1, 1)
        self.label = QtGui.QLabel(LookupTranslatorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.vl_notification = QtGui.QVBoxLayout()
        self.vl_notification.setObjectName(_fromUtf8("vl_notification"))
        self.gridLayout.addLayout(self.vl_notification, 0, 0, 1, 2)

        self.retranslateUi(LookupTranslatorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupTranslatorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupTranslatorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupTranslatorDialog)

    def retranslateUi(self, LookupTranslatorDialog):
        LookupTranslatorDialog.setWindowTitle(QtGui.QApplication.translate("LookupTranslatorDialog", "Lookup Translator Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("LookupTranslatorDialog", "Default lookup value", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LookupTranslatorDialog", "Lookup table", None, QtGui.QApplication.UnicodeUTF8))

