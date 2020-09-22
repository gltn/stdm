# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_photo_data_source.ui'
#
# Created: Sun Jul 24 19:10:02 2016
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PhotoDataSourceEditor(object):
    def setupUi(self, PhotoDataSourceEditor):
        PhotoDataSourceEditor.setObjectName(_fromUtf8("PhotoDataSourceEditor"))
        PhotoDataSourceEditor.resize(276, 298)
        self.gridLayout = QtGui.QGridLayout(PhotoDataSourceEditor)
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vl_notification = QtGui.QVBoxLayout()
        self.vl_notification.setObjectName(_fromUtf8("vl_notification"))
        self.gridLayout.addLayout(self.vl_notification, 1, 0, 1, 2)
        self.label_4 = QtGui.QLabel(PhotoDataSourceEditor)
        self.label_4.setStyleSheet(_fromUtf8("padding: 2px; font-weight: bold; background-color: rgb(200, 200, 200);"))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 118, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(PhotoDataSourceEditor)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.ref_table = ReferencedTableEditor(self.groupBox)
        self.ref_table.setObjectName(_fromUtf8("ref_table"))
        self.gridLayout_2.addWidget(self.ref_table, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 2)
        self.label = QtGui.QLabel(PhotoDataSourceEditor)
        self.label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.cbo_document_type = QtGui.QComboBox(PhotoDataSourceEditor)
        self.cbo_document_type.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_document_type.setObjectName(_fromUtf8("cbo_document_type"))
        self.gridLayout.addWidget(self.cbo_document_type, 3, 1, 1, 1)

        self.retranslateUi(PhotoDataSourceEditor)
        QtCore.QMetaObject.connectSlotsByName(PhotoDataSourceEditor)

    def retranslateUi(self, PhotoDataSourceEditor):
        PhotoDataSourceEditor.setWindowTitle(QtGui.QApplication.translate("PhotoDataSourceEditor", "Photo Data Source Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("PhotoDataSourceEditor", "Photo", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PhotoDataSourceEditor", "Linked Table Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PhotoDataSourceEditor", "Document type", None, QtGui.QApplication.UnicodeUTF8))

from .referenced_table_editor import ReferencedTableEditor
