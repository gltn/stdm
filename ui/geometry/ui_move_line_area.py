# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geometry_container.ui'
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

class Ui_GeometryContainer(object):
    def setupUi(self, GeometryContainer):
        GeometryContainer.setObjectName(_fromUtf8("GeometryContainer"))
        GeometryContainer.resize(354, 435)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.dockWidgetContents)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 1, 1, 1)
        self.geom_tools_widgets = QtGui.QStackedWidget(self.dockWidgetContents)
        self.geom_tools_widgets.setObjectName(_fromUtf8("geom_tools_widgets"))
        self.page_1 = QtGui.QWidget()
        self.page_1.setObjectName(_fromUtf8("page_1"))
        self.gridLayout_3 = QtGui.QGridLayout(self.page_1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_6 = QtGui.QLabel(self.page_1)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 0, 0, 1, 2)
        self.split_poly_area = QtGui.QLineEdit(self.page_1)
        self.split_poly_area.setObjectName(_fromUtf8("split_poly_area"))
        self.gridLayout_3.addWidget(self.split_poly_area, 0, 2, 1, 2)
        self.pushButton = QtGui.QPushButton(self.page_1)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_3.addWidget(self.pushButton, 3, 0, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.page_1)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout_3.addWidget(self.pushButton_2, 3, 1, 1, 2)
        self.pushButton_3 = QtGui.QPushButton(self.page_1)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.gridLayout_3.addWidget(self.pushButton_3, 3, 3, 1, 1)
        self.geom_tools_widgets.addWidget(self.page_1)
        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName(_fromUtf8("page_3"))
        self.gridLayout_2 = QtGui.QGridLayout(self.page_3)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_10 = QtGui.QLabel(self.page_3)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_2.addWidget(self.label_10, 1, 0, 1, 1)
        self.radioButton = QtGui.QRadioButton(self.page_3)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.gridLayout_2.addWidget(self.radioButton, 1, 1, 1, 1)
        self.radioButton_2 = QtGui.QRadioButton(self.page_3)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.gridLayout_2.addWidget(self.radioButton_2, 1, 2, 1, 1)
        self.label_11 = QtGui.QLabel(self.page_3)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)
        self.lineEdit_2 = QtGui.QLineEdit(self.page_3)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.gridLayout_2.addWidget(self.lineEdit_2, 0, 1, 1, 2)
        self.pushButton_4 = QtGui.QPushButton(self.page_3)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout_2.addWidget(self.pushButton_4, 2, 2, 1, 1)
        self.pushButton_5 = QtGui.QPushButton(self.page_3)
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.gridLayout_2.addWidget(self.pushButton_5, 2, 1, 1, 1)
        self.pushButton_6 = QtGui.QPushButton(self.page_3)
        self.pushButton_6.setObjectName(_fromUtf8("pushButton_6"))
        self.gridLayout_2.addWidget(self.pushButton_6, 2, 0, 1, 1)
        self.geom_tools_widgets.addWidget(self.page_3)
        self.gridLayout.addWidget(self.geom_tools_widgets, 1, 0, 2, 4)
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.geom_tools_combo = QtGui.QComboBox(self.dockWidgetContents)
        self.geom_tools_combo.setObjectName(_fromUtf8("geom_tools_combo"))
        self.geom_tools_combo.addItem(_fromUtf8(""))
        self.geom_tools_combo.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.geom_tools_combo, 0, 1, 1, 3)
        self.label_5 = QtGui.QLabel(self.dockWidgetContents)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.dockWidgetContents)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        GeometryContainer.setWidget(self.dockWidgetContents)

        self.retranslateUi(GeometryContainer)
        self.geom_tools_widgets.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GeometryContainer)

    def retranslateUi(self, GeometryContainer):
        GeometryContainer.setWindowTitle(_translate("GeometryContainer", "Geometry Tools", None))
        self.label_2.setText(_translate("GeometryContainer", "Selected Features:", None))
        self.label_4.setText(_translate("GeometryContainer", "TextLabel", None))
        self.label_6.setText(_translate("GeometryContainer", "Split polygon area:", None))
        self.pushButton.setText(_translate("GeometryContainer", "Cancel", None))
        self.pushButton_2.setText(_translate("GeometryContainer", "Preview", None))
        self.pushButton_3.setText(_translate("GeometryContainer", "Save", None))
        self.label_10.setText(_translate("GeometryContainer", "Offset side:", None))
        self.radioButton.setText(_translate("GeometryContainer", "Left", None))
        self.radioButton_2.setText(_translate("GeometryContainer", "Right", None))
        self.label_11.setText(_translate("GeometryContainer", "Offset distance:", None))
        self.pushButton_4.setText(_translate("GeometryContainer", "Save", None))
        self.pushButton_5.setText(_translate("GeometryContainer", "Preview", None))
        self.pushButton_6.setText(_translate("GeometryContainer", "Cancel", None))
        self.label.setText(_translate("GeometryContainer", "Geometry tools:", None))
        self.geom_tools_combo.setItemText(0, _translate("GeometryContainer", "Split Polyon: Move Line and Area", None))
        self.geom_tools_combo.setItemText(1, _translate("GeometryContainer", "Split Polygon: Offset Distance", None))
        self.label_5.setText(_translate("GeometryContainer", "TextLabel", None))
        self.label_3.setText(_translate("GeometryContainer", "Maximum area:", None))

