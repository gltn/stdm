# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_spatial_unit_manager.ui'
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

class Ui_SpatialUnitManagerWidget(object):
    def setupUi(self, SpatialUnitManagerWidget):
        SpatialUnitManagerWidget.setObjectName(_fromUtf8("SpatialUnitManagerWidget"))
        SpatialUnitManagerWidget.resize(405, 392)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem = QtGui.QSpacerItem(20, 119, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 4, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.import_gpx_file_button = QtGui.QPushButton(self.groupBox_2)
        self.import_gpx_file_button.setObjectName(_fromUtf8("import_gpx_file_button"))
        self.gridLayout_3.addWidget(self.import_gpx_file_button, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_2, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox.setSizeIncrement(QtCore.QSize(0, 200))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.stdm_layers_combo = QtGui.QComboBox(self.groupBox)
        self.stdm_layers_combo.setSizeIncrement(QtCore.QSize(0, 0))
        self.stdm_layers_combo.setMinimumContentsLength(3)
        self.stdm_layers_combo.setIconSize(QtCore.QSize(16, 16))
        self.stdm_layers_combo.setObjectName(_fromUtf8("stdm_layers_combo"))
        self.gridLayout.addWidget(self.stdm_layers_combo, 0, 1, 1, 1)
        self.add_to_canvas_button = QtGui.QPushButton(self.groupBox)
        self.add_to_canvas_button.setObjectName(_fromUtf8("add_to_canvas_button"))
        self.gridLayout.addWidget(self.add_to_canvas_button, 1, 0, 1, 2)
        self.set_display_name_button = QtGui.QPushButton(self.groupBox)
        self.set_display_name_button.setObjectName(_fromUtf8("set_display_name_button"))
        self.gridLayout.addWidget(self.set_display_name_button, 2, 0, 1, 2)
        self.layerLebel = QtGui.QLabel(self.groupBox)
        self.layerLebel.setMaximumSize(QtCore.QSize(70, 16777215))
        self.layerLebel.setObjectName(_fromUtf8("layerLebel"))
        self.gridLayout.addWidget(self.layerLebel, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 1)
        self.NotificationBar = QtGui.QVBoxLayout()
        self.NotificationBar.setObjectName(_fromUtf8("NotificationBar"))
        self.gridLayout_2.addLayout(self.NotificationBar, 0, 0, 1, 1)
        SpatialUnitManagerWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(SpatialUnitManagerWidget)
        QtCore.QMetaObject.connectSlotsByName(SpatialUnitManagerWidget)

    def retranslateUi(self, SpatialUnitManagerWidget):
        SpatialUnitManagerWidget.setWindowTitle(_translate("SpatialUnitManagerWidget", "DockWidget", None))
        self.groupBox_2.setTitle(_translate("SpatialUnitManagerWidget", "Import Feature:", None))
        self.import_gpx_file_button.setText(_translate("SpatialUnitManagerWidget", "GPS Feature Import", None))
        self.groupBox.setTitle(_translate("SpatialUnitManagerWidget", "Manage Layers:", None))
        self.add_to_canvas_button.setText(_translate("SpatialUnitManagerWidget", "Add Layer to Canvas", None))
        self.set_display_name_button.setText(_translate("SpatialUnitManagerWidget", "Set Display Name", None))
        self.layerLebel.setText(_translate("SpatialUnitManagerWidget", "Layer", None))

