# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lookup_value_selector.ui'
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

class Ui_LookupValueSelector(object):
    def setupUi(self, LookupValueSelector):
        LookupValueSelector.setObjectName(_fromUtf8("LookupValueSelector"))
        LookupValueSelector.resize(295, 283)
        self.verticalLayout = QtGui.QVBoxLayout(LookupValueSelector)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.notice_bar = QtGui.QVBoxLayout()
        self.notice_bar.setObjectName(_fromUtf8("notice_bar"))
        self.verticalLayout.addLayout(self.notice_bar)
        self.value_list_box = QtGui.QTreeView(LookupValueSelector)
        self.value_list_box.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.value_list_box.setAlternatingRowColors(True)
        self.value_list_box.setRootIsDecorated(False)
        self.value_list_box.setUniformRowHeights(True)
        self.value_list_box.setObjectName(_fromUtf8("value_list_box"))
        self.verticalLayout.addWidget(self.value_list_box)
        self.buttonBox = QtGui.QDialogButtonBox(LookupValueSelector)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LookupValueSelector)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LookupValueSelector.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LookupValueSelector.reject)
        QtCore.QMetaObject.connectSlotsByName(LookupValueSelector)

    def retranslateUi(self, LookupValueSelector):
        LookupValueSelector.setWindowTitle(_translate("LookupValueSelector", " Lookup Entity Code Selector", None))

