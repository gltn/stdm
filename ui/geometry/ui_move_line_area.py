# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_move_line_area.ui'
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

class Ui_MoveLineArea(object):
    def setupUi(self, MoveLineArea):
        MoveLineArea.setObjectName(_fromUtf8("MoveLineArea"))
        MoveLineArea.resize(337, 299)
        self.gridLayout = QtGui.QGridLayout(MoveLineArea)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_6 = QtGui.QLabel(MoveLineArea)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.pushButton_6 = QtGui.QPushButton(MoveLineArea)
        self.pushButton_6.setObjectName(_fromUtf8("pushButton_6"))
        self.gridLayout.addWidget(self.pushButton_6, 3, 0, 1, 1)
        self.doubleSpinBox_3 = QtGui.QDoubleSpinBox(MoveLineArea)
        self.doubleSpinBox_3.setObjectName(_fromUtf8("doubleSpinBox_3"))
        self.gridLayout.addWidget(self.doubleSpinBox_3, 2, 1, 1, 3)
        self.pushButton_5 = QtGui.QPushButton(MoveLineArea)
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.gridLayout.addWidget(self.pushButton_5, 3, 1, 1, 1)
        self.pushButton_4 = QtGui.QPushButton(MoveLineArea)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout.addWidget(self.pushButton_4, 3, 3, 1, 1)
        self.label_30 = QtGui.QLabel(MoveLineArea)
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.gridLayout.addWidget(self.label_30, 1, 0, 1, 1)
        self.label_23 = QtGui.QLabel(MoveLineArea)
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.gridLayout.addWidget(self.label_23, 0, 1, 1, 1)
        self.label_22 = QtGui.QLabel(MoveLineArea)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.gridLayout.addWidget(self.label_22, 0, 0, 1, 1)
        self.label_31 = QtGui.QLabel(MoveLineArea)
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.gridLayout.addWidget(self.label_31, 1, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)

        self.retranslateUi(MoveLineArea)
        QtCore.QMetaObject.connectSlotsByName(MoveLineArea)

    def retranslateUi(self, MoveLineArea):
        MoveLineArea.setWindowTitle(_translate("MoveLineArea", "Form", None))
        self.label_6.setText(_translate("MoveLineArea", "Split polygon area:", None))
        self.pushButton_6.setText(_translate("MoveLineArea", "Cancel", None))
        self.pushButton_5.setText(_translate("MoveLineArea", "Preview", None))
        self.pushButton_4.setText(_translate("MoveLineArea", "Save", None))
        self.label_30.setText(_translate("MoveLineArea", "Selected line:", None))
        self.label_23.setText(_translate("MoveLineArea", "0", None))
        self.label_22.setText(_translate("MoveLineArea", "Selected features:", None))
        self.label_31.setText(_translate("MoveLineArea", "0", None))

