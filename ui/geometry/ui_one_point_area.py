# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_one_point_area.ui'
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

class Ui_OnePointArea(object):
    def setupUi(self, OnePointArea):
        OnePointArea.setObjectName(_fromUtf8("OnePointArea"))
        OnePointArea.resize(346, 380)
        self.gridLayout = QtGui.QGridLayout(OnePointArea)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_2 = QtGui.QGroupBox(OnePointArea)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.radioButton_3 = QtGui.QRadioButton(self.groupBox_2)
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.gridLayout_7.addWidget(self.radioButton_3, 0, 0, 1, 1)
        self.radioButton_4 = QtGui.QRadioButton(self.groupBox_2)
        self.radioButton_4.setObjectName(_fromUtf8("radioButton_4"))
        self.gridLayout_7.addWidget(self.radioButton_4, 1, 0, 1, 1)
        self.label_16 = QtGui.QLabel(self.groupBox_2)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_7.addWidget(self.label_16, 2, 0, 1, 1)
        self.doubleSpinBox_4 = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_4.setObjectName(_fromUtf8("doubleSpinBox_4"))
        self.gridLayout_7.addWidget(self.doubleSpinBox_4, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 4, 0, 1, 3)
        self.preview_btn = QtGui.QPushButton(OnePointArea)
        self.preview_btn.setObjectName(_fromUtf8("preview_btn"))
        self.gridLayout.addWidget(self.preview_btn, 6, 1, 1, 1)
        self.label_2 = QtGui.QLabel(OnePointArea)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.sel_features_lbl = QtGui.QLabel(OnePointArea)
        self.sel_features_lbl.setObjectName(_fromUtf8("sel_features_lbl"))
        self.gridLayout.addWidget(self.sel_features_lbl, 0, 1, 1, 1)
        self.selected_line_lbl = QtGui.QLabel(OnePointArea)
        self.selected_line_lbl.setObjectName(_fromUtf8("selected_line_lbl"))
        self.gridLayout.addWidget(self.selected_line_lbl, 1, 1, 1, 2)
        self.label_18 = QtGui.QLabel(OnePointArea)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.gridLayout.addWidget(self.label_18, 1, 0, 1, 1)
        self.label_17 = QtGui.QLabel(OnePointArea)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout.addWidget(self.label_17, 2, 0, 1, 1)
        self.label_19 = QtGui.QLabel(OnePointArea)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.gridLayout.addWidget(self.label_19, 2, 1, 1, 2)
        self.label_3 = QtGui.QLabel(OnePointArea)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_4 = QtGui.QLabel(OnePointArea)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 1, 1, 1)
        self.label_21 = QtGui.QLabel(OnePointArea)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.gridLayout.addWidget(self.label_21, 5, 0, 1, 1)
        self.doubleSpinBox_5 = QtGui.QDoubleSpinBox(OnePointArea)
        self.doubleSpinBox_5.setObjectName(_fromUtf8("doubleSpinBox_5"))
        self.gridLayout.addWidget(self.doubleSpinBox_5, 5, 1, 1, 2)
        self.cancel_btn = QtGui.QPushButton(OnePointArea)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.gridLayout.addWidget(self.cancel_btn, 6, 0, 1, 1)
        self.save_btn = QtGui.QPushButton(OnePointArea)
        self.save_btn.setObjectName(_fromUtf8("save_btn"))
        self.gridLayout.addWidget(self.save_btn, 6, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 1, 1, 1)

        self.retranslateUi(OnePointArea)
        QtCore.QMetaObject.connectSlotsByName(OnePointArea)

    def retranslateUi(self, OnePointArea):
        OnePointArea.setWindowTitle(_translate("OnePointArea", "Form", None))
        self.groupBox_2.setTitle(_translate("OnePointArea", "Reference Point", None))
        self.radioButton_3.setText(_translate("OnePointArea", "RadioButton", None))
        self.radioButton_4.setText(_translate("OnePointArea", "RadioButton", None))
        self.label_16.setText(_translate("OnePointArea", "Length from reference point:", None))
        self.preview_btn.setText(_translate("OnePointArea", "Preview", None))
        self.label_2.setText(_translate("OnePointArea", "Selected Features:", None))
        self.sel_features_lbl.setText(_translate("OnePointArea", "0", None))
        self.selected_line_lbl.setText(_translate("OnePointArea", "0", None))
        self.label_18.setText(_translate("OnePointArea", "Selected line:", None))
        self.label_17.setText(_translate("OnePointArea", "Total length:", None))
        self.label_19.setText(_translate("OnePointArea", "0", None))
        self.label_3.setText(_translate("OnePointArea", "Selected points:", None))
        self.label_4.setText(_translate("OnePointArea", "0", None))
        self.label_21.setText(_translate("OnePointArea", "Split polygon area:", None))
        self.cancel_btn.setText(_translate("OnePointArea", "Cancel", None))
        self.save_btn.setText(_translate("OnePointArea", "Save", None))

