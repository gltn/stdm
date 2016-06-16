# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_column_depend.ui'
#
# Created: Tue Jun 14 17:54:17 2016
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

class Ui_dlgColumnDepend(object):
    def setupUi(self, dlgColumnDepend):
        dlgColumnDepend.setObjectName(_fromUtf8("dlgColumnDepend"))
        dlgColumnDepend.setWindowModality(QtCore.Qt.WindowModal)
        dlgColumnDepend.resize(358, 296)
        dlgColumnDepend.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.verticalLayout = QtGui.QVBoxLayout(dlgColumnDepend)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(dlgColumnDepend)
        self.label.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/warning_large.png")))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.qryLabel = QtGui.QLabel(dlgColumnDepend)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.qryLabel.setFont(font)
        self.qryLabel.setTextFormat(QtCore.Qt.PlainText)
        self.qryLabel.setWordWrap(True)
        self.qryLabel.setObjectName(_fromUtf8("qryLabel"))
        self.horizontalLayout_3.addWidget(self.qryLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.twEntityDepend = QtGui.QTreeWidget(dlgColumnDepend)
        self.twEntityDepend.setObjectName(_fromUtf8("twEntityDepend"))
        self.twEntityDepend.headerItem().setText(0, _fromUtf8("1"))
        self.twEntityDepend.header().setVisible(False)
        self.verticalLayout.addWidget(self.twEntityDepend)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(165, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnCancel = QtGui.QPushButton(dlgColumnDepend)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout.addWidget(self.btnCancel)
        self.btnDelete = QtGui.QPushButton(dlgColumnDepend)
        self.btnDelete.setObjectName(_fromUtf8("btnDelete"))
        self.horizontalLayout.addWidget(self.btnDelete)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(dlgColumnDepend)
        QtCore.QMetaObject.connectSlotsByName(dlgColumnDepend)

    def retranslateUi(self, dlgColumnDepend):
        dlgColumnDepend.setWindowTitle(_translate("dlgColumnDepend", "Column dependencies", None))
        self.qryLabel.setText(_translate("dlgColumnDepend", "The following items depend on the \'%s\' column;\n"
" deleting it might affect the data stored in these dependent\n"
" objects and in some cases, might also lead to their deletion.\n"
"Click \'Delete column\' to proceed.", None))
        self.btnCancel.setText(_translate("dlgColumnDepend", "Cancel", None))
        self.btnDelete.setText(_translate("dlgColumnDepend", "Delete column", None))

import resources_rc
