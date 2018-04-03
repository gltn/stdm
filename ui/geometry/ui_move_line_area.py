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
        self.cancel_btn = QtGui.QPushButton(MoveLineArea)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.gridLayout.addWidget(self.cancel_btn, 3, 1, 1, 1)
        self.split_polygon_area = QtGui.QDoubleSpinBox(MoveLineArea)
        self.split_polygon_area.setMaximum(9999999.0)
        self.split_polygon_area.setObjectName(_fromUtf8("split_polygon_area"))
        self.gridLayout.addWidget(self.split_polygon_area, 2, 2, 1, 3)
        self.preview_btn = QtGui.QPushButton(MoveLineArea)
        self.preview_btn.setObjectName(_fromUtf8("preview_btn"))
        self.gridLayout.addWidget(self.preview_btn, 3, 2, 1, 1)
        self.run_btn = QtGui.QPushButton(MoveLineArea)
        self.run_btn.setObjectName(_fromUtf8("run_btn"))
        self.gridLayout.addWidget(self.run_btn, 3, 4, 1, 1)
        self.sel_features_lbl = QtGui.QLabel(MoveLineArea)
        self.sel_features_lbl.setObjectName(_fromUtf8("sel_features_lbl"))
        self.gridLayout.addWidget(self.sel_features_lbl, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.selected_line_lbl = QtGui.QLabel(MoveLineArea)
        self.selected_line_lbl.setObjectName(_fromUtf8("selected_line_lbl"))
        self.gridLayout.addWidget(self.selected_line_lbl, 1, 2, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.label_22 = QtGui.QLabel(MoveLineArea)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.gridLayout.addWidget(self.label_22, 0, 0, 1, 2)
        self.label_30 = QtGui.QLabel(MoveLineArea)
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.gridLayout.addWidget(self.label_30, 1, 0, 1, 2)
        self.label_6 = QtGui.QLabel(MoveLineArea)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 2)

        self.retranslateUi(MoveLineArea)
        QtCore.QMetaObject.connectSlotsByName(MoveLineArea)

    def retranslateUi(self, MoveLineArea):
        MoveLineArea.setWindowTitle(_translate("MoveLineArea", "Form", None))
        self.cancel_btn.setText(_translate("MoveLineArea", "Cancel", None))
        self.split_polygon_area.setSuffix(_translate("MoveLineArea", " Sq Meters", None))
        self.preview_btn.setText(_translate("MoveLineArea", "Preview", None))
        self.run_btn.setText(_translate("MoveLineArea", "Run", None))
        self.sel_features_lbl.setText(_translate("MoveLineArea", "0", None))
        self.selected_line_lbl.setText(_translate("MoveLineArea", "0", None))
        self.label_22.setText(_translate("MoveLineArea", "Selected features:", None))
        self.label_30.setText(_translate("MoveLineArea", "Selected line:", None))
        self.label_6.setText(_translate("MoveLineArea", "Split polygon area:", None))

