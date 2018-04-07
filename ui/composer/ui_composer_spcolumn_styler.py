# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_spcolumn_styler.ui'
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

class Ui_frmComposerSpatialColumnEditor(object):
    def setupUi(self, frmComposerSpatialColumnEditor):
        frmComposerSpatialColumnEditor.setObjectName(_fromUtf8("frmComposerSpatialColumnEditor"))
        frmComposerSpatialColumnEditor.resize(334, 366)
        self.gridLayout = QtGui.QGridLayout(frmComposerSpatialColumnEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(frmComposerSpatialColumnEditor)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.general = QtGui.QWidget()
        self.general.setObjectName(_fromUtf8("general"))
        self.gridLayout_2 = QtGui.QGridLayout(self.general)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.general)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(-1, -1, -1, 15)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.cboLabelField = QtGui.QComboBox(self.groupBox)
        self.cboLabelField.setMinimumSize(QtCore.QSize(0, 30))
        self.cboLabelField.setObjectName(_fromUtf8("cboLabelField"))
        self.verticalLayout.addWidget(self.cboLabelField)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.general)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 15)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.sb_zoom = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.sb_zoom.setMinimumSize(QtCore.QSize(0, 32))
        self.sb_zoom.setMaximum(16.0)
        self.sb_zoom.setProperty("value", 1.5)
        self.sb_zoom.setObjectName(_fromUtf8("sb_zoom"))
        self.verticalLayout_2.addWidget(self.sb_zoom)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 72, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)
        self.tabWidget.addTab(self.general, _fromUtf8(""))
        self.style = QtGui.QWidget()
        self.style.setObjectName(_fromUtf8("style"))
        self.gridLayout_3 = QtGui.QGridLayout(self.style)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.styleScrollArea = QtGui.QScrollArea(self.style)
        self.styleScrollArea.setWidgetResizable(True)
        self.styleScrollArea.setObjectName(_fromUtf8("styleScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 282, 292))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_5 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.styleLayout = QtGui.QGridLayout()
        self.styleLayout.setObjectName(_fromUtf8("styleLayout"))
        self.gridLayout_5.addLayout(self.styleLayout, 0, 0, 1, 1)
        self.styleScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.styleScrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.style, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(frmComposerSpatialColumnEditor)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmComposerSpatialColumnEditor)

    def retranslateUi(self, frmComposerSpatialColumnEditor):
        frmComposerSpatialColumnEditor.setWindowTitle(_translate("frmComposerSpatialColumnEditor", "Spatial Column Style Editor", None))
        self.groupBox.setTitle(_translate("frmComposerSpatialColumnEditor", "Legend Label:", None))
        self.label_2.setText(_translate("frmComposerSpatialColumnEditor", "<html><head/><body><p>Select the field whose value will be used to label the feature in the composer legend</p></body></html>", None))
        self.groupBox_2.setTitle(_translate("frmComposerSpatialColumnEditor", "Feature Zoom:", None))
        self.label.setText(_translate("frmComposerSpatialColumnEditor", "Specify the zoom out level of the feature relative to the fulll extent of the map", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general), _translate("frmComposerSpatialColumnEditor", "General", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.style), _translate("frmComposerSpatialColumnEditor", "Style", None))
