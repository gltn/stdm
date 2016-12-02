# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_gps_tool.ui'
#
# Created: Tue Nov 22 17:01:57 2016
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(588, 480)
        Dialog.setModal(False)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setContentsMargins(0, 5, 5, 5)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gpx_data_source_groupbox = QtGui.QGroupBox(Dialog)
        self.gpx_data_source_groupbox.setObjectName(_fromUtf8("gpx_data_source_groupbox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gpx_data_source_groupbox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gpx_file_layout = QtGui.QHBoxLayout()
        self.gpx_file_layout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gpx_file_layout.setObjectName(_fromUtf8("gpx_file_layout"))
        self.file_lb = QtGui.QLabel(self.gpx_data_source_groupbox)
        self.file_lb.setObjectName(_fromUtf8("file_lb"))
        self.gpx_file_layout.addWidget(self.file_lb)
        self.file_le = QgsFileDropEdit(self.gpx_data_source_groupbox)
        self.file_le.setObjectName(_fromUtf8("file_le"))
        self.gpx_file_layout.addWidget(self.file_le)
        self.file_select_bt = QtGui.QPushButton(self.gpx_data_source_groupbox)
        self.file_select_bt.setObjectName(_fromUtf8("file_select_bt"))
        self.gpx_file_layout.addWidget(self.file_select_bt)
        self.gridLayout_2.addLayout(self.gpx_file_layout, 0, 0, 1, 1)
        self.gpx_feature_type_layout = QtGui.QHBoxLayout()
        self.gpx_feature_type_layout.setObjectName(_fromUtf8("gpx_feature_type_layout"))
        self.feature_type_lb = QtGui.QLabel(self.gpx_data_source_groupbox)
        self.feature_type_lb.setObjectName(_fromUtf8("feature_type_lb"))
        self.gpx_feature_type_layout.addWidget(self.feature_type_lb)
        self.feature_type_cb = QtGui.QComboBox(self.gpx_data_source_groupbox)
        self.feature_type_cb.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.feature_type_cb.sizePolicy().hasHeightForWidth())
        self.feature_type_cb.setSizePolicy(sizePolicy)
        # self.feature_type_cb.setCurrentText(_fromUtf8(""))
        self.feature_type_cb.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.feature_type_cb.setObjectName(_fromUtf8("feature_type_cb"))
        self.feature_type_cb.addItem(_fromUtf8(""))
        self.feature_type_cb.addItem(_fromUtf8(""))
        self.feature_type_cb.addItem(_fromUtf8(""))
        self.gpx_feature_type_layout.addWidget(self.feature_type_cb)
        self.gridLayout_2.addLayout(self.gpx_feature_type_layout, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.gpx_data_source_groupbox)
        self.gpx_table_groupbox = QtGui.QGroupBox(Dialog)
        self.gpx_table_groupbox.setObjectName(_fromUtf8("gpx_table_groupbox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.gpx_table_groupbox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gpx_table_layout = QtGui.QHBoxLayout()
        self.gpx_table_layout.setObjectName(_fromUtf8("gpx_table_layout"))
        self.table_widget_layout = QtGui.QVBoxLayout()
        self.table_widget_layout.setObjectName(_fromUtf8("table_widget_layout"))
        self.table_widget = QtGui.QTableWidget(self.gpx_table_groupbox)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setObjectName(_fromUtf8("table_widget"))
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.table_widget.horizontalHeader().setCascadingSectionResizes(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setCascadingSectionResizes(True)
        self.table_widget_layout.addWidget(self.table_widget)
        self.gpx_table_layout.addLayout(self.table_widget_layout)
        self.table_button_layout = QtGui.QVBoxLayout()
        self.table_button_layout.setObjectName(_fromUtf8("table_button_layout"))
        self.select_all_bt = QtGui.QPushButton(self.gpx_table_groupbox)
        self.select_all_bt.setEnabled(False)
        self.select_all_bt.setObjectName(_fromUtf8("select_all_bt"))
        self.table_button_layout.addWidget(self.select_all_bt)
        self.clear_all_bt = QtGui.QPushButton(self.gpx_table_groupbox)
        self.clear_all_bt.setEnabled(False)
        self.clear_all_bt.setObjectName(_fromUtf8("clear_all_bt"))
        self.table_button_layout.addWidget(self.clear_all_bt)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.table_button_layout.addItem(spacerItem)
        self.gpx_table_layout.addLayout(self.table_button_layout)
        self.gridLayout_3.addLayout(self.gpx_table_layout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.gpx_table_groupbox)
        self.gpx_load_layout = QtGui.QHBoxLayout()
        self.gpx_load_layout.setObjectName(_fromUtf8("gpx_load_layout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gpx_load_layout.addItem(spacerItem1)
        self.load_bt = QtGui.QPushButton(Dialog)
        self.load_bt.setEnabled(False)
        self.load_bt.setObjectName(_fromUtf8("load_bt"))
        self.gpx_load_layout.addWidget(self.load_bt)
        self.cancel_bt = QtGui.QPushButton(Dialog)
        self.cancel_bt.setObjectName(_fromUtf8("cancel_bt"))
        self.gpx_load_layout.addWidget(self.cancel_bt)
        self.verticalLayout.addLayout(self.gpx_load_layout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.feature_type_cb.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.file_le, self.file_select_bt)
        Dialog.setTabOrder(self.file_select_bt, self.feature_type_cb)
        Dialog.setTabOrder(self.feature_type_cb, self.table_widget)
        Dialog.setTabOrder(self.table_widget, self.select_all_bt)
        Dialog.setTabOrder(self.select_all_bt, self.clear_all_bt)
        Dialog.setTabOrder(self.clear_all_bt, self.load_bt)
        Dialog.setTabOrder(self.load_bt, self.cancel_bt)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "GPS Data Import", None))
        self.gpx_data_source_groupbox.setTitle(_translate("Dialog", "Data Source", None))
        self.file_lb.setText(_translate("Dialog", "File:", None))
        self.file_select_bt.setText(_translate("Dialog", "Browse...", None))
        self.feature_type_lb.setText(_translate("Dialog", "Feature Type:", None))
        self.feature_type_cb.setItemText(0, _translate("Dialog", "Waypoint", None))
        self.feature_type_cb.setItemText(1, _translate("Dialog", "Track", None))
        self.feature_type_cb.setItemText(2, _translate("Dialog", "Route", None))
        self.gpx_table_groupbox.setTitle(_translate("Dialog", "Data View", None))
        self.select_all_bt.setText(_translate("Dialog", "Select All", None))
        self.clear_all_bt.setText(_translate("Dialog", "Clear All", None))
        self.load_bt.setText(_translate("Dialog", "Load", None))
        self.cancel_bt.setText(_translate("Dialog", "Cancel", None))

from qgis.gui import QgsFileDropEdit
