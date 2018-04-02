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
        OnePointArea.resize(387, 380)
        self.gridLayout = QtGui.QGridLayout(OnePointArea)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(OnePointArea)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 6, 0, 1, 1)
        self.label_2 = QtGui.QLabel(OnePointArea)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.preview_btn = QtGui.QPushButton(OnePointArea)
        self.preview_btn.setObjectName(_fromUtf8("preview_btn"))
        self.gridLayout.addWidget(self.preview_btn, 8, 1, 1, 1)
        self.label_18 = QtGui.QLabel(OnePointArea)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.gridLayout.addWidget(self.label_18, 1, 0, 1, 1)
        self.line_length_lbl = QtGui.QLabel(OnePointArea)
        self.line_length_lbl.setObjectName(_fromUtf8("line_length_lbl"))
        self.gridLayout.addWidget(self.line_length_lbl, 2, 1, 1, 2)
        self.selected_line_lbl = QtGui.QLabel(OnePointArea)
        self.selected_line_lbl.setObjectName(_fromUtf8("selected_line_lbl"))
        self.gridLayout.addWidget(self.selected_line_lbl, 1, 1, 1, 2)
        self.label_17 = QtGui.QLabel(OnePointArea)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout.addWidget(self.label_17, 2, 0, 1, 1)
        self.label_21 = QtGui.QLabel(OnePointArea)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.gridLayout.addWidget(self.label_21, 5, 0, 1, 1)
        self.label_3 = QtGui.QLabel(OnePointArea)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.split_polygon_area = QtGui.QDoubleSpinBox(OnePointArea)
        self.split_polygon_area.setObjectName(_fromUtf8("split_polygon_area"))
        self.gridLayout.addWidget(self.split_polygon_area, 5, 1, 1, 2)
        self.cancel_btn = QtGui.QPushButton(OnePointArea)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.gridLayout.addWidget(self.cancel_btn, 8, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 1, 1, 1)
        self.save_btn = QtGui.QPushButton(OnePointArea)
        self.save_btn.setObjectName(_fromUtf8("save_btn"))
        self.gridLayout.addWidget(self.save_btn, 8, 2, 1, 1)
        self.label_16 = QtGui.QLabel(OnePointArea)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout.addWidget(self.label_16, 4, 0, 1, 1)
        self.length_from_point = QtGui.QDoubleSpinBox(OnePointArea)
        self.length_from_point.setObjectName(_fromUtf8("length_from_point"))
        self.gridLayout.addWidget(self.length_from_point, 4, 1, 1, 2)
        self.clockwise = QtGui.QRadioButton(OnePointArea)
        self.clockwise.setChecked(True)
        self.clockwise.setObjectName(_fromUtf8("clockwise"))
        self.gridLayout.addWidget(self.clockwise, 6, 1, 1, 1)
        self.anticlockwise = QtGui.QRadioButton(OnePointArea)
        self.anticlockwise.setObjectName(_fromUtf8("anticlockwise"))
        self.gridLayout.addWidget(self.anticlockwise, 7, 1, 1, 1)
        self.selected_points_lbl = QtGui.QLabel(OnePointArea)
        self.selected_points_lbl.setObjectName(_fromUtf8("selected_points_lbl"))
        self.gridLayout.addWidget(self.selected_points_lbl, 3, 1, 1, 2)
        self.sel_features_lbl = QtGui.QLabel(OnePointArea)
        self.sel_features_lbl.setObjectName(_fromUtf8("sel_features_lbl"))
        self.gridLayout.addWidget(self.sel_features_lbl, 0, 1, 1, 2)

        self.retranslateUi(OnePointArea)
        QtCore.QMetaObject.connectSlotsByName(OnePointArea)

    def retranslateUi(self, OnePointArea):
        OnePointArea.setWindowTitle(_translate("OnePointArea", "Form", None))
        self.label.setText(_translate("OnePointArea", "Direction:", None))
        self.label_2.setText(_translate("OnePointArea", "Selected features:", None))
        self.preview_btn.setText(_translate("OnePointArea", "Preview", None))
        self.label_18.setText(_translate("OnePointArea", "Selected line:", None))
        self.line_length_lbl.setText(_translate("OnePointArea", "0", None))
        self.selected_line_lbl.setText(_translate("OnePointArea", "0", None))
        self.label_17.setText(_translate("OnePointArea", "Total length:", None))
        self.label_21.setText(_translate("OnePointArea", "Split polygon area:", None))
        self.label_3.setText(_translate("OnePointArea", "Selected points:", None))
        self.cancel_btn.setText(_translate("OnePointArea", "Cancel", None))
        self.save_btn.setText(_translate("OnePointArea", "Save", None))
        self.label_16.setText(_translate("OnePointArea", "Length from reference point:", None))
        self.clockwise.setText(_translate("OnePointArea", "Clockwise", None))
        self.anticlockwise.setText(_translate("OnePointArea", "Anti-clockwise", None))
        self.selected_points_lbl.setText(_translate("OnePointArea", "0", None))
        self.sel_features_lbl.setText(_translate("OnePointArea", "0", None))

