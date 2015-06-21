# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_chart_vertical_bar.ui'
#
# Created: Thu May 07 11:57:50 2015
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

class Ui_VerticalBarGraphSettings(object):
    def setupUi(self, VerticalBarGraphSettings):
        VerticalBarGraphSettings.setObjectName(_fromUtf8("VerticalBarGraphSettings"))
        VerticalBarGraphSettings.resize(275, 422)
        self.gridLayout = QtGui.QGridLayout(VerticalBarGraphSettings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(VerticalBarGraphSettings)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 6, 0, 1, 1)
        self.txt_x_label = QtGui.QLineEdit(VerticalBarGraphSettings)
        self.txt_x_label.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_x_label.setMaxLength(100)
        self.txt_x_label.setObjectName(_fromUtf8("txt_x_label"))
        self.gridLayout.addWidget(self.txt_x_label, 5, 0, 1, 1)
        self.label_3 = QtGui.QLabel(VerticalBarGraphSettings)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(VerticalBarGraphSettings)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.cbo_x_field = QtGui.QComboBox(VerticalBarGraphSettings)
        self.cbo_x_field.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_x_field.setObjectName(_fromUtf8("cbo_x_field"))
        self.gridLayout.addWidget(self.cbo_x_field, 3, 0, 1, 1)
        self.txt_y_label = QtGui.QLineEdit(VerticalBarGraphSettings)
        self.txt_y_label.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_y_label.setMaxLength(100)
        self.txt_y_label.setObjectName(_fromUtf8("txt_y_label"))
        self.gridLayout.addWidget(self.txt_y_label, 7, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(VerticalBarGraphSettings)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.cbo_value_field = QtGui.QComboBox(self.groupBox)
        self.cbo_value_field.setMinimumSize(QtCore.QSize(100, 30))
        self.cbo_value_field.setObjectName(_fromUtf8("cbo_value_field"))
        self.gridLayout_2.addWidget(self.cbo_value_field, 0, 1, 1, 1)
        self.btn_add_value_field = QtGui.QToolButton(self.groupBox)
        self.btn_add_value_field.setMinimumSize(QtCore.QSize(30, 30))
        self.btn_add_value_field.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_add_value_field.setIcon(icon)
        self.btn_add_value_field.setObjectName(_fromUtf8("btn_add_value_field"))
        self.gridLayout_2.addWidget(self.btn_add_value_field, 0, 2, 1, 1)
        self.btn_reset_value_fields = QtGui.QToolButton(self.groupBox)
        self.btn_reset_value_fields.setMinimumSize(QtCore.QSize(30, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/reset.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_reset_value_fields.setIcon(icon1)
        self.btn_reset_value_fields.setObjectName(_fromUtf8("btn_reset_value_fields"))
        self.gridLayout_2.addWidget(self.btn_reset_value_fields, 0, 3, 1, 1)
        self.tb_value_config = QtGui.QTabWidget(self.groupBox)
        self.tb_value_config.setMinimumSize(QtCore.QSize(0, 120))
        self.tb_value_config.setTabsClosable(True)
        self.tb_value_config.setMovable(True)
        self.tb_value_config.setObjectName(_fromUtf8("tb_value_config"))
        self.gridLayout_2.addWidget(self.tb_value_config, 1, 0, 1, 4)
        self.gridLayout.addWidget(self.groupBox, 8, 0, 1, 1)

        self.retranslateUi(VerticalBarGraphSettings)
        QtCore.QMetaObject.connectSlotsByName(VerticalBarGraphSettings)

    def retranslateUi(self, VerticalBarGraphSettings):
        VerticalBarGraphSettings.setWindowTitle(_translate("VerticalBarGraphSettings", "Vertical Bar Graph Settings", None))
        self.label_2.setText(_translate("VerticalBarGraphSettings", "Y label", None))
        self.label_3.setText(_translate("VerticalBarGraphSettings", "X field", None))
        self.label_4.setText(_translate("VerticalBarGraphSettings", "X label", None))
        self.groupBox.setTitle(_translate("VerticalBarGraphSettings", "Value Configuration:", None))
        self.label.setText(_translate("VerticalBarGraphSettings", "Value field", None))
        self.btn_reset_value_fields.setText(_translate("VerticalBarGraphSettings", "...", None))

import resources_rc
