# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_chart_config.ui'
#
# Created: Wed May 27 22:48:01 2015
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ChartPropertiesEditor(object):
    def setupUi(self, ChartPropertiesEditor):
        ChartPropertiesEditor.setObjectName(_fromUtf8("ChartPropertiesEditor"))
        ChartPropertiesEditor.resize(340, 749)
        self.gridLayout = QtGui.QGridLayout(ChartPropertiesEditor)
        self.gridLayout.setContentsMargins(5, 2, 5, 2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ChartPropertiesEditor)
        self.label.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label.setMargin(7)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.Chart = QtGui.QLabel(ChartPropertiesEditor)
        self.Chart.setStyleSheet(_fromUtf8("padding: 2px; font-weight: bold; background-color: rgb(200, 200, 200);"))
        self.Chart.setObjectName(_fromUtf8("Chart"))
        self.gridLayout.addWidget(self.Chart, 0, 0, 1, 2)
        self.cbo_chart_type = QtGui.QComboBox(ChartPropertiesEditor)
        self.cbo_chart_type.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_chart_type.setObjectName(_fromUtf8("cbo_chart_type"))
        self.gridLayout.addWidget(self.cbo_chart_type, 2, 1, 1, 1)
        self.scrollArea = QtGui.QScrollArea(ChartPropertiesEditor)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 330, 678))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_5 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.groupBox = QgsCollapsibleGroupBoxBasic(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setMargin(5)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.ref_table = ReferencedTableEditor(self.groupBox)
        self.ref_table.setObjectName(_fromUtf8("ref_table"))
        self.gridLayout_2.addWidget(self.ref_table, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QgsCollapsibleGroupBoxBasic(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setMargin(1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.series_type_container = QtGui.QStackedWidget(self.groupBox_2)
        self.series_type_container.setFrameShape(QtGui.QFrame.NoFrame)
        self.series_type_container.setObjectName(_fromUtf8("series_type_container"))
        self.gridLayout_3.addWidget(self.series_type_container, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QgsCollapsibleGroupBoxBasic(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setContentsMargins(9, 6, 9, 6)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setMinimumSize(QtCore.QSize(60, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_4.addWidget(self.label_2, 0, 0, 1, 1)
        self.txt_plot_title = QtGui.QLineEdit(self.groupBox_3)
        self.txt_plot_title.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_plot_title.setMaxLength(200)
        self.txt_plot_title.setObjectName(_fromUtf8("txt_plot_title"))
        self.gridLayout_4.addWidget(self.txt_plot_title, 0, 1, 1, 1)
        self.gb_legend = QtGui.QGroupBox(self.groupBox_3)
        self.gb_legend.setMinimumSize(QtCore.QSize(0, 0))
        self.gb_legend.setFlat(False)
        self.gb_legend.setCheckable(True)
        self.gb_legend.setChecked(False)
        self.gb_legend.setObjectName(_fromUtf8("gb_legend"))
        self.gridLayout_6 = QtGui.QGridLayout(self.gb_legend)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_3 = QtGui.QLabel(self.gb_legend)
        self.label_3.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_6.addWidget(self.label_3, 0, 0, 1, 1)
        self.cbo_legend_pos = QtGui.QComboBox(self.gb_legend)
        self.cbo_legend_pos.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_legend_pos.setObjectName(_fromUtf8("cbo_legend_pos"))
        self.gridLayout_6.addWidget(self.cbo_legend_pos, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.gb_legend, 1, 0, 1, 2)
        self.gridLayout_5.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 3, 0, 1, 2)
        self.vl_notification = QtGui.QVBoxLayout()
        self.vl_notification.setObjectName(_fromUtf8("vl_notification"))
        self.gridLayout.addLayout(self.vl_notification, 1, 0, 1, 2)

        self.retranslateUi(ChartPropertiesEditor)
        QtCore.QMetaObject.connectSlotsByName(ChartPropertiesEditor)

    def retranslateUi(self, ChartPropertiesEditor):
        ChartPropertiesEditor.setWindowTitle(_translate("ChartPropertiesEditor", "Chart Properties Editor", None))
        self.label.setText(_translate("ChartPropertiesEditor", "Type", None))
        self.Chart.setText(_translate("ChartPropertiesEditor", "Chart", None))
        self.groupBox.setTitle(_translate("ChartPropertiesEditor", "Data Source", None))
        self.groupBox_2.setTitle(_translate("ChartPropertiesEditor", "Series Properties", None))
        self.groupBox_3.setTitle(_translate("ChartPropertiesEditor", "Graph Properties", None))
        self.label_2.setText(_translate("ChartPropertiesEditor", "Title", None))
        self.gb_legend.setTitle(_translate("ChartPropertiesEditor", "Insert legend", None))
        self.label_3.setText(_translate("ChartPropertiesEditor", "Position", None))

from .referenced_table_editor import ReferencedTableEditor
from qgis.gui import QgsCollapsibleGroupBoxBasic
