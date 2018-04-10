# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_show_measurements.ui'
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

class Ui_ShowMeasurements(object):
    def setupUi(self, ShowMeasurements):
        ShowMeasurements.setObjectName(_fromUtf8("ShowMeasurements"))
        ShowMeasurements.resize(416, 256)
        self.gridLayout = QtGui.QGridLayout(ShowMeasurements)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.run_btn = QtGui.QPushButton(ShowMeasurements)
        self.run_btn.setObjectName(_fromUtf8("run_btn"))
        self.gridLayout.addWidget(self.run_btn, 4, 5, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 3, 1, 1)
        self.label_2 = QtGui.QLabel(ShowMeasurements)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)
        self.label = QtGui.QLabel(ShowMeasurements)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.length_chk = QtGui.QCheckBox(ShowMeasurements)
        self.length_chk.setChecked(True)
        self.length_chk.setObjectName(_fromUtf8("length_chk"))
        self.gridLayout.addWidget(self.length_chk, 1, 2, 1, 2)
        self.area_chk = QtGui.QCheckBox(ShowMeasurements)
        self.area_chk.setObjectName(_fromUtf8("area_chk"))
        self.gridLayout.addWidget(self.area_chk, 1, 4, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(116, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 1)
        self.selected_features_rad = QtGui.QRadioButton(ShowMeasurements)
        self.selected_features_rad.setChecked(True)
        self.selected_features_rad.setObjectName(_fromUtf8("selected_features_rad"))
        self.gridLayout.addWidget(self.selected_features_rad, 3, 2, 1, 2)
        self.selected_layer_rad = QtGui.QRadioButton(ShowMeasurements)
        self.selected_layer_rad.setObjectName(_fromUtf8("selected_layer_rad"))
        self.gridLayout.addWidget(self.selected_layer_rad, 3, 4, 1, 2)
        self.cancel_btn = QtGui.QPushButton(ShowMeasurements)
        self.cancel_btn.setObjectName(_fromUtf8("cancel_btn"))
        self.gridLayout.addWidget(self.cancel_btn, 4, 3, 1, 1)

        self.retranslateUi(ShowMeasurements)
        QtCore.QMetaObject.connectSlotsByName(ShowMeasurements)

    def retranslateUi(self, ShowMeasurements):
        ShowMeasurements.setWindowTitle(_translate("ShowMeasurements", "Form", None))
        self.run_btn.setText(_translate("ShowMeasurements", "Run", None))
        self.label_2.setText(_translate("ShowMeasurements", "Show measurements:", None))
        self.label.setText(_translate("ShowMeasurements", "Apply on:", None))
        self.length_chk.setText(_translate("ShowMeasurements", "Length", None))
        self.area_chk.setText(_translate("ShowMeasurements", "Area", None))
        self.selected_features_rad.setText(_translate("ShowMeasurements", "Selected Features", None))
        self.selected_layer_rad.setText(_translate("ShowMeasurements", "Selected Layer", None))
        self.cancel_btn.setText(_translate("ShowMeasurements", "Cancel", None))

