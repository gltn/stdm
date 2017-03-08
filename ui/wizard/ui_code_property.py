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
        CodeProperty.resize(354, 143)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CodeProperty.sizePolicy().hasHeightForWidth())
        CodeProperty.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(CodeProperty)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(CodeProperty)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.prefix_source_cbo = QtGui.QComboBox(CodeProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prefix_source_cbo.sizePolicy().hasHeightForWidth())
        self.prefix_source_cbo.setSizePolicy(sizePolicy)
        self.prefix_source_cbo.setMinimumSize(QtCore.QSize(249, 0))
        self.prefix_source_cbo.setMaximumSize(QtCore.QSize(16777215, 22))
        self.prefix_source_cbo.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.prefix_source_cbo.setObjectName(_fromUtf8("prefix_source_cbo"))
        self.horizontalLayout.addWidget(self.prefix_source_cbo)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_3 = QtGui.QLabel(CodeProperty)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.separator_cbo = QtGui.QComboBox(CodeProperty)
        self.separator_cbo.setMinimumSize(QtCore.QSize(249, 0))
        self.separator_cbo.setObjectName(_fromUtf8("separator_cbo"))
        self.horizontalLayout_3.addWidget(self.separator_cbo)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(CodeProperty)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.leading_zero_cbo = QtGui.QComboBox(CodeProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leading_zero_cbo.sizePolicy().hasHeightForWidth())
        self.leading_zero_cbo.setSizePolicy(sizePolicy)
        self.leading_zero_cbo.setMinimumSize(QtCore.QSize(249, 0))
        self.leading_zero_cbo.setObjectName(_fromUtf8("leading_zero_cbo"))
        self.horizontalLayout_2.addWidget(self.leading_zero_cbo)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(CodeProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(CodeProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CodeProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CodeProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(CodeProperty)

    def retranslateUi(self, CodeProperty):
        CodeProperty.setWindowTitle(_translate("CodeProperty", "Auto Generated Code Property", None))
        self.label.setText(_translate("CodeProperty", "Prefix source", None))
        self.label_3.setText(_translate("CodeProperty", "Separator", None))
        self.label_2.setText(_translate("CodeProperty", "Leading zero", None))

