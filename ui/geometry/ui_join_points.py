# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_join_points.ui'
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

class Ui_JoinPoints(object):
    def setupUi(self, JoinPoints):
        JoinPoints.setObjectName(_fromUtf8("JoinPoints"))
        JoinPoints.resize(400, 272)
        self.gridLayout = QtGui.QGridLayout(JoinPoints)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_8 = QtGui.QLabel(JoinPoints)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)
        self.sel_features_lbl = QtGui.QLabel(JoinPoints)
        self.sel_features_lbl.setObjectName(_fromUtf8("sel_features_lbl"))
        self.gridLayout.addWidget(self.sel_features_lbl, 0, 1, 1, 1)
        self.label_26 = QtGui.QLabel(JoinPoints)
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.gridLayout.addWidget(self.label_26, 0, 0, 1, 1)
        self.selected_line_lbl = QtGui.QLabel(JoinPoints)
        self.selected_line_lbl.setObjectName(_fromUtf8("selected_line_lbl"))
        self.gridLayout.addWidget(self.selected_line_lbl, 1, 1, 1, 1)
        self.label_14 = QtGui.QLabel(JoinPoints)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout.addWidget(self.label_14, 3, 0, 1, 1)
        self.label_15 = QtGui.QLabel(JoinPoints)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout.addWidget(self.label_15, 3, 1, 1, 1)
        self.label_12 = QtGui.QLabel(JoinPoints)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout.addWidget(self.label_12, 2, 1, 1, 1)
        self.label_7 = QtGui.QLabel(JoinPoints)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.preview_btn = QtGui.QPushButton(JoinPoints)
        self.preview_btn.setObjectName(_fromUtf8("preview_btn"))
        self.gridLayout.addWidget(self.preview_btn, 5, 1, 1, 1)
        self.cancel_btn = QtGui.QPushButton(JoinPoints)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.gridLayout.addWidget(self.cancel_btn, 5, 0, 1, 1)
        self.save_btn = QtGui.QPushButton(JoinPoints)
        self.save_btn.setObjectName(_fromUtf8("save_btn"))
        self.gridLayout.addWidget(self.save_btn, 5, 2, 1, 1)
        self.groupBox = QtGui.QGroupBox(JoinPoints)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.radioButton = QtGui.QRadioButton(self.groupBox)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.gridLayout_6.addWidget(self.radioButton, 0, 0, 1, 1)
        self.radioButton_2 = QtGui.QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.gridLayout_6.addWidget(self.radioButton_2, 1, 0, 1, 1)
        self.label_13 = QtGui.QLabel(self.groupBox)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_6.addWidget(self.label_13, 2, 0, 1, 1)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox.setObjectName(_fromUtf8("doubleSpinBox"))
        self.gridLayout_6.addWidget(self.doubleSpinBox, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 4, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)

        self.retranslateUi(JoinPoints)
        QtCore.QMetaObject.connectSlotsByName(JoinPoints)

    def retranslateUi(self, JoinPoints):
        JoinPoints.setWindowTitle(_translate("JoinPoints", "Form", None))
        self.label_8.setText(_translate("JoinPoints", "Selected line:", None))
        self.sel_features_lbl.setText(_translate("JoinPoints", "0", None))
        self.label_26.setText(_translate("JoinPoints", "Selected features:", None))
        self.selected_line_lbl.setText(_translate("JoinPoints", "0", None))
        self.label_14.setText(_translate("JoinPoints", "Selected points:", None))
        self.label_15.setText(_translate("JoinPoints", "0", None))
        self.label_12.setText(_translate("JoinPoints", "0", None))
        self.label_7.setText(_translate("JoinPoints", "Total length:", None))
        self.preview_btn.setText(_translate("JoinPoints", "Preview", None))
        self.cancel_btn.setText(_translate("JoinPoints", "Cancel", None))
        self.save_btn.setText(_translate("JoinPoints", "Save", None))
        self.groupBox.setTitle(_translate("JoinPoints", "Reference Point", None))
        self.radioButton.setText(_translate("JoinPoints", "RadioButton", None))
        self.radioButton_2.setText(_translate("JoinPoints", "RadioButton", None))
        self.label_13.setText(_translate("JoinPoints", "Length from reference point:", None))

