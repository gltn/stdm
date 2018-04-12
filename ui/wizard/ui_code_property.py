# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_code_property.ui'
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

class Ui_CodeProperty(object):
    def setupUi(self, CodeProperty):
        CodeProperty.setObjectName(_fromUtf8("CodeProperty"))
        CodeProperty.resize(491, 404)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CodeProperty.sizePolicy().hasHeightForWidth())
        CodeProperty.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(CodeProperty)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.disable_auto_increment_lbl = QtGui.QLabel(CodeProperty)
        self.disable_auto_increment_lbl.setObjectName(_fromUtf8("disable_auto_increment_lbl"))
        self.gridLayout.addWidget(self.disable_auto_increment_lbl, 4, 0, 1, 2)
        self.label = QtGui.QLabel(CodeProperty)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.enable_editing_lbl = QtGui.QLabel(CodeProperty)
        self.enable_editing_lbl.setObjectName(_fromUtf8("enable_editing_lbl"))
        self.gridLayout.addWidget(self.enable_editing_lbl, 6, 0, 1, 2)
        self.enable_editing_chk = QtGui.QCheckBox(CodeProperty)
        self.enable_editing_chk.setText(_fromUtf8(""))
        self.enable_editing_chk.setObjectName(_fromUtf8("enable_editing_chk"))
        self.gridLayout.addWidget(self.enable_editing_chk, 6, 2, 1, 1)
        self.label_2 = QtGui.QLabel(CodeProperty)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 5, 0, 1, 2)
        self.disable_auto_increment_chk = QtGui.QCheckBox(CodeProperty)
        self.disable_auto_increment_chk.setText(_fromUtf8(""))
        self.disable_auto_increment_chk.setChecked(False)
        self.disable_auto_increment_chk.setObjectName(_fromUtf8("disable_auto_increment_chk"))
        self.gridLayout.addWidget(self.disable_auto_increment_chk, 4, 2, 1, 1)
        self.leading_zero_cbo = QtGui.QComboBox(CodeProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leading_zero_cbo.sizePolicy().hasHeightForWidth())
        self.leading_zero_cbo.setSizePolicy(sizePolicy)
        self.leading_zero_cbo.setMinimumSize(QtCore.QSize(249, 0))
        self.leading_zero_cbo.setObjectName(_fromUtf8("leading_zero_cbo"))
        self.gridLayout.addWidget(self.leading_zero_cbo, 5, 2, 1, 3)
        self.separator_cbo = QtGui.QComboBox(CodeProperty)
        self.separator_cbo.setMinimumSize(QtCore.QSize(249, 0))
        self.separator_cbo.setObjectName(_fromUtf8("separator_cbo"))
        self.gridLayout.addWidget(self.separator_cbo, 3, 2, 1, 3)
        self.column_code_view = QtGui.QTableView(CodeProperty)
        self.column_code_view.setObjectName(_fromUtf8("column_code_view"))
        self.gridLayout.addWidget(self.column_code_view, 2, 0, 1, 5)
        self.prefix_source_cbo = QtGui.QComboBox(CodeProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prefix_source_cbo.sizePolicy().hasHeightForWidth())
        self.prefix_source_cbo.setSizePolicy(sizePolicy)
        self.prefix_source_cbo.setMinimumSize(QtCore.QSize(249, 0))
        self.prefix_source_cbo.setMaximumSize(QtCore.QSize(16777215, 22))
        self.prefix_source_cbo.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.prefix_source_cbo.setObjectName(_fromUtf8("prefix_source_cbo"))
        self.gridLayout.addWidget(self.prefix_source_cbo, 0, 2, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(CodeProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 3, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 3)
        self.label_3 = QtGui.QLabel(CodeProperty)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 2)

        self.retranslateUi(CodeProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CodeProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CodeProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(CodeProperty)

    def retranslateUi(self, CodeProperty):
        CodeProperty.setWindowTitle(_translate("CodeProperty", "Auto Generated Code Property", None))
        self.disable_auto_increment_lbl.setText(_translate("CodeProperty", "Disable auto increment number:", None))
        self.label.setText(_translate("CodeProperty", "Prefix source:", None))
        self.enable_editing_lbl.setText(_translate("CodeProperty", "Enable editing:", None))
        self.label_2.setText(_translate("CodeProperty", "Auto increment leading zero:", None))
        self.label_3.setText(_translate("CodeProperty", "Separtor:", None))

