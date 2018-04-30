# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_equal_area.ui'
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

class Ui_EqualArea(object):
    def setupUi(self, EqualArea):
        EqualArea.setObjectName(_fromUtf8("EqualArea"))
        EqualArea.resize(399, 380)
        self.gridLayout = QtGui.QGridLayout(EqualArea)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 12, 0, 1, 4)
        self.label_4 = QtGui.QLabel(EqualArea)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 2)
        self.splitted_area_lbl = QtGui.QLabel(EqualArea)
        self.splitted_area_lbl.setObjectName(_fromUtf8("splitted_area_lbl"))
        self.gridLayout.addWidget(self.splitted_area_lbl, 4, 2, 1, 2)
        self.selected_line_lbl = QtGui.QLabel(EqualArea)
        self.selected_line_lbl.setObjectName(_fromUtf8("selected_line_lbl"))
        self.gridLayout.addWidget(self.selected_line_lbl, 1, 2, 1, 2)
        self.preview_btn = QtGui.QPushButton(EqualArea)
        self.preview_btn.setObjectName(_fromUtf8("preview_btn"))
        self.gridLayout.addWidget(self.preview_btn, 11, 2, 1, 1)
        self.line_length_lbl = QtGui.QLabel(EqualArea)
        self.line_length_lbl.setObjectName(_fromUtf8("line_length_lbl"))
        self.gridLayout.addWidget(self.line_length_lbl, 2, 2, 1, 2)
        self.cancel_btn = QtGui.QPushButton(EqualArea)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.gridLayout.addWidget(self.cancel_btn, 11, 1, 1, 1)
        self.sel_features_lbl = QtGui.QLabel(EqualArea)
        self.sel_features_lbl.setObjectName(_fromUtf8("sel_features_lbl"))
        self.gridLayout.addWidget(self.sel_features_lbl, 0, 2, 1, 2)
        self.label_2 = QtGui.QLabel(EqualArea)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 11, 0, 1, 1)
        self.run_btn = QtGui.QPushButton(EqualArea)
        self.run_btn.setObjectName(_fromUtf8("run_btn"))
        self.gridLayout.addWidget(self.run_btn, 11, 3, 1, 1)
        self.label_17 = QtGui.QLabel(EqualArea)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout.addWidget(self.label_17, 2, 0, 1, 2)
        self.label_18 = QtGui.QLabel(EqualArea)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.gridLayout.addWidget(self.label_18, 1, 0, 1, 2)
        self.label = QtGui.QLabel(EqualArea)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 2)
        self.label_21 = QtGui.QLabel(EqualArea)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.gridLayout.addWidget(self.label_21, 6, 0, 1, 2)
        self.features_area_lbl = QtGui.QLabel(EqualArea)
        self.features_area_lbl.setObjectName(_fromUtf8("features_area_lbl"))
        self.gridLayout.addWidget(self.features_area_lbl, 3, 2, 1, 2)
        self.parellel_rad = QtGui.QRadioButton(EqualArea)
        self.parellel_rad.setChecked(True)
        self.parellel_rad.setObjectName(_fromUtf8("parellel_rad"))
        self.gridLayout.addWidget(self.parellel_rad, 6, 2, 1, 2)
        self.equal_boundary_rad = QtGui.QRadioButton(EqualArea)
        self.equal_boundary_rad.setObjectName(_fromUtf8("equal_boundary_rad"))
        self.gridLayout.addWidget(self.equal_boundary_rad, 7, 2, 1, 2)
        self.label_16 = QtGui.QLabel(EqualArea)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout.addWidget(self.label_16, 5, 0, 1, 1)
        self.number_of_polygons = QtGui.QSpinBox(EqualArea)
        self.number_of_polygons.setMinimum(1)
        self.number_of_polygons.setObjectName(_fromUtf8("number_of_polygons"))
        self.gridLayout.addWidget(self.number_of_polygons, 5, 2, 1, 2)

        self.retranslateUi(EqualArea)
        QtCore.QMetaObject.connectSlotsByName(EqualArea)

    def retranslateUi(self, EqualArea):
        EqualArea.setWindowTitle(_translate("EqualArea", "Form", None))
        self.label_4.setText(_translate("EqualArea", "Selected features area:", None))
        self.splitted_area_lbl.setText(_translate("EqualArea", "0", None))
        self.selected_line_lbl.setText(_translate("EqualArea", "0", None))
        self.preview_btn.setText(_translate("EqualArea", "Preview", None))
        self.line_length_lbl.setText(_translate("EqualArea", "0", None))
        self.cancel_btn.setText(_translate("EqualArea", "Cancel", None))
        self.sel_features_lbl.setText(_translate("EqualArea", "0", None))
        self.label_2.setText(_translate("EqualArea", "Selected features:", None))
        self.run_btn.setText(_translate("EqualArea", "Run", None))
        self.label_17.setText(_translate("EqualArea", "Total length:", None))
        self.label_18.setText(_translate("EqualArea", "Selected line:", None))
        self.label.setText(_translate("EqualArea", "Splitted polygon area:", None))
        self.label_21.setText(_translate("EqualArea", "Method:", None))
        self.features_area_lbl.setText(_translate("EqualArea", "0", None))
        self.parellel_rad.setText(_translate("EqualArea", "Parellel to a Line", None))
        self.equal_boundary_rad.setText(_translate("EqualArea", "Equal Boundary at Side", None))
        self.label_16.setText(_translate("EqualArea", "Number of polygons:", None))

