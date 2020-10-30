# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_symbol_editor.ui'
#
# Created: Sun May 25 19:08:02 2014
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

class Ui_frmComposerSymbolEditor(object):
    def setupUi(self, frmComposerSymbolEditor):
        frmComposerSymbolEditor.setObjectName(_fromUtf8("frmComposerSymbolEditor"))
        frmComposerSymbolEditor.resize(340, 320)
        self.gridLayout = QtGui.QGridLayout(frmComposerSymbolEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(frmComposerSymbolEditor)
        self.label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cboSpatialFields = QtGui.QComboBox(frmComposerSymbolEditor)
        self.cboSpatialFields.setMinimumSize(QtCore.QSize(0, 30))
        self.cboSpatialFields.setObjectName(_fromUtf8("cboSpatialFields"))
        self.gridLayout.addWidget(self.cboSpatialFields, 0, 1, 1, 1)
        self.btnAddField = QtGui.QPushButton(frmComposerSymbolEditor)
        self.btnAddField.setMaximumSize(QtCore.QSize(30, 30))
        self.btnAddField.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAddField.setIcon(icon)
        self.btnAddField.setObjectName(_fromUtf8("btnAddField"))
        self.gridLayout.addWidget(self.btnAddField, 0, 2, 1, 1)
        self.btnClear = QtGui.QPushButton(frmComposerSymbolEditor)
        self.btnClear.setMaximumSize(QtCore.QSize(30, 30))
        self.btnClear.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/reset.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnClear.setIcon(icon1)
        self.btnClear.setObjectName(_fromUtf8("btnClear"))
        self.gridLayout.addWidget(self.btnClear, 0, 3, 1, 1)
        self.tbFieldProperties = QtGui.QTabWidget(frmComposerSymbolEditor)
        self.tbFieldProperties.setTabsClosable(True)
        self.tbFieldProperties.setObjectName(_fromUtf8("tbFieldProperties"))
        self.gridLayout.addWidget(self.tbFieldProperties, 1, 0, 1, 4)

        self.retranslateUi(frmComposerSymbolEditor)
        self.tbFieldProperties.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(frmComposerSymbolEditor)

    def retranslateUi(self, frmComposerSymbolEditor):
        frmComposerSymbolEditor.setWindowTitle(_translate("frmComposerSymbolEditor", "Composer Field Editor", None))
        self.label.setText(_translate("frmComposerSymbolEditor", "Spatial Field", None))
        self.btnAddField.setToolTip(_translate("frmComposerSymbolEditor", "Add Field", None))
        self.btnClear.setToolTip(_translate("frmComposerSymbolEditor", "Clear Fields", None))
