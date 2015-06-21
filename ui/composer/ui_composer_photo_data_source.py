# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_photo_data_source.ui'
#
# Created: Mon Jan 05 09:56:02 2015
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_PhotoDataSourceEditor(object):
    def setupUi(self, PhotoDataSourceEditor):
        PhotoDataSourceEditor.setObjectName(_fromUtf8("PhotoDataSourceEditor"))
        PhotoDataSourceEditor.resize(276, 298)
        self.gridLayout = QtGui.QGridLayout(PhotoDataSourceEditor)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vl_notification = QtGui.QVBoxLayout()
        self.vl_notification.setObjectName(_fromUtf8("vl_notification"))
        self.gridLayout.addLayout(self.vl_notification, 1, 0, 1, 2)
        self.label_4 = QtGui.QLabel(PhotoDataSourceEditor)
        self.label_4.setStyleSheet(_fromUtf8("padding: 2px; font-weight: bold; background-color: rgb(200, 200, 200);"))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 118, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.ref_table = ReferencedTableEditor(PhotoDataSourceEditor)
        self.ref_table.setObjectName(_fromUtf8("ref_table"))
        self.gridLayout.addWidget(self.ref_table, 2, 0, 1, 2)

        self.retranslateUi(PhotoDataSourceEditor)
        QtCore.QMetaObject.connectSlotsByName(PhotoDataSourceEditor)

    def retranslateUi(self, PhotoDataSourceEditor):
        PhotoDataSourceEditor.setWindowTitle(_translate("PhotoDataSourceEditor", "Photo Data Source Editor", None))
        self.label_4.setText(_translate("PhotoDataSourceEditor", "Photo", None))

from .referenced_table_editor import ReferencedTableEditor
