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
        SpatialUnitManagerWidget.resize(405, 285)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SpatialUnitManagerWidget.sizePolicy().hasHeightForWidth())
        SpatialUnitManagerWidget.setSizePolicy(sizePolicy)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.feature_details_btn = QtGui.QToolButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.feature_details_btn.sizePolicy().hasHeightForWidth())
        self.feature_details_btn.setSizePolicy(sizePolicy)
        self.feature_details_btn.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/feature_details.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.feature_details_btn.setIcon(icon)
        self.feature_details_btn.setCheckable(True)
        self.feature_details_btn.setObjectName(_fromUtf8("feature_details_btn"))
        self.verticalLayout.addWidget(self.feature_details_btn)
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox.setSizeIncrement(QtCore.QSize(0, 200))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.layerLebel = QtGui.QLabel(self.groupBox)
        self.layerLebel.setMaximumSize(QtCore.QSize(70, 16777215))
        self.layerLebel.setObjectName(_fromUtf8("layerLebel"))
        self.gridLayout.addWidget(self.layerLebel, 1, 0, 1, 1)
        self.stdm_layers_combo = QtGui.QComboBox(self.groupBox)
        self.stdm_layers_combo.setMinimumSize(QtCore.QSize(30, 22))
        self.stdm_layers_combo.setSizeIncrement(QtCore.QSize(0, 0))
        self.stdm_layers_combo.setMinimumContentsLength(3)
        self.stdm_layers_combo.setIconSize(QtCore.QSize(16, 16))
        self.stdm_layers_combo.setObjectName(_fromUtf8("stdm_layers_combo"))
        self.gridLayout.addWidget(self.stdm_layers_combo, 1, 1, 1, 1)
        self.add_to_canvas_button = QtGui.QPushButton(self.groupBox)
        self.add_to_canvas_button.setMinimumSize(QtCore.QSize(300, 26))
        self.add_to_canvas_button.setObjectName(_fromUtf8("add_to_canvas_button"))
        self.gridLayout.addWidget(self.add_to_canvas_button, 2, 0, 1, 2)
        self.set_display_name_button = QtGui.QPushButton(self.groupBox)
        self.set_display_name_button.setMinimumSize(QtCore.QSize(30, 26))
        self.set_display_name_button.setObjectName(_fromUtf8("set_display_name_button"))
        self.gridLayout.addWidget(self.set_display_name_button, 3, 0, 1, 2)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.import_gpx_file_button = QtGui.QPushButton(self.groupBox_2)
        self.import_gpx_file_button.setMinimumSize(QtCore.QSize(30, 26))
        self.import_gpx_file_button.setObjectName(_fromUtf8("import_gpx_file_button"))
        self.gridLayout_3.addWidget(self.import_gpx_file_button, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        SpatialUnitManagerWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(SpatialUnitManagerWidget)
        QtCore.QMetaObject.connectSlotsByName(SpatialUnitManagerWidget)

    def retranslateUi(self, SpatialUnitManagerWidget):
        SpatialUnitManagerWidget.setWindowTitle(_translate("SpatialUnitManagerWidget", "DockWidget", None))
        self.feature_details_btn.setToolTip(_translate("SpatialUnitManagerWidget", "Feature details", None))
        self.feature_details_btn.setAccessibleName(_translate("SpatialUnitManagerWidget", "Tool", None))
        self.feature_details_btn.setText(_translate("SpatialUnitManagerWidget", "Feature Details", None))
        self.groupBox.setTitle(_translate("SpatialUnitManagerWidget", "Manage Layers:", None))
        self.layerLebel.setText(_translate("SpatialUnitManagerWidget", "Layer", None))
        self.add_to_canvas_button.setText(_translate("SpatialUnitManagerWidget", "Add Layer to Canvas", None))
        self.set_display_name_button.setText(_translate("SpatialUnitManagerWidget", "Set Display Name", None))
        self.groupBox_2.setTitle(_translate("SpatialUnitManagerWidget", "Import Feature:", None))
        self.import_gpx_file_button.setText(_translate("SpatialUnitManagerWidget", "From GPX File...", None))

from stdm import resources_rc
