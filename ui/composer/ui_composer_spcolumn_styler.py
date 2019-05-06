# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Kahiu\.qgis2\python\plugins\stdm\ui\composer\ui_composer_spcolumn_styler.ui'
#
# Created: Sat May  4 10:25:50 2019
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmComposerSpatialColumnEditor(object):
    def setupUi(self, frmComposerSpatialColumnEditor):
        frmComposerSpatialColumnEditor.setObjectName(_fromUtf8("frmComposerSpatialColumnEditor"))
        frmComposerSpatialColumnEditor.resize(1364, 900)
        self.gridLayout = QtGui.QGridLayout(frmComposerSpatialColumnEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(frmComposerSpatialColumnEditor)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.general = QtGui.QWidget()
        self.general.setObjectName(_fromUtf8("general"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.general)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
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
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.general)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.rb_relative_zoom = QtGui.QRadioButton(self.groupBox_2)
        self.rb_relative_zoom.setChecked(False)
        self.rb_relative_zoom.setAutoExclusive(True)
        self.rb_relative_zoom.setObjectName(_fromUtf8("rb_relative_zoom"))
        self.gridLayout_4.addWidget(self.rb_relative_zoom, 0, 0, 1, 1)
        self.sb_zoom = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.sb_zoom.setMinimumSize(QtCore.QSize(0, 32))
        self.sb_zoom.setMaximumSize(QtCore.QSize(300, 16777215))
        self.sb_zoom.setMaximum(16.0)
        self.sb_zoom.setProperty("value", 1.5)
        self.sb_zoom.setObjectName(_fromUtf8("sb_zoom"))
        self.gridLayout_4.addWidget(self.sb_zoom, 0, 1, 1, 1)
        self.rb_fixed_scale = QtGui.QRadioButton(self.groupBox_2)
        self.rb_fixed_scale.setObjectName(_fromUtf8("rb_fixed_scale"))
        self.gridLayout_4.addWidget(self.rb_fixed_scale, 1, 0, 1, 1)
        self.sb_fixed_zoom = QtGui.QSpinBox(self.groupBox_2)
        self.sb_fixed_zoom.setMinimumSize(QtCore.QSize(0, 32))
        self.sb_fixed_zoom.setMaximum(1000000)
        self.sb_fixed_zoom.setSingleStep(500)
        self.sb_fixed_zoom.setProperty("value", 1000)
        self.sb_fixed_zoom.setObjectName(_fromUtf8("sb_fixed_zoom"))
        self.gridLayout_4.addWidget(self.sb_fixed_zoom, 1, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 485, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabWidget.addTab(self.general, _fromUtf8(""))
        self.style = QtGui.QWidget()
        self.style.setObjectName(_fromUtf8("style"))
        self.gridLayout_3 = QtGui.QGridLayout(self.style)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.styleScrollArea = QtGui.QScrollArea(self.style)
        self.styleScrollArea.setWidgetResizable(True)
        self.styleScrollArea.setObjectName(_fromUtf8("styleScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1284, 787))
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
        frmComposerSpatialColumnEditor.setWindowTitle(QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "Spatial Column Style Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "Legend Label:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "<html><head/><body><p>Select the field whose value will be used to label the feature in the composer legend</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "Feature Zoom:", None, QtGui.QApplication.UnicodeUTF8))
        self.rb_relative_zoom.setText(QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "Zoom relative to the full map extents", None, QtGui.QApplication.UnicodeUTF8))
        self.rb_fixed_scale.setText(QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "Fixed scale", None, QtGui.QApplication.UnicodeUTF8))
        self.sb_fixed_zoom.setPrefix(QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "1:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general), QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "General", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.style), QtGui.QApplication.translate("frmComposerSpatialColumnEditor", "Style", None, QtGui.QApplication.UnicodeUTF8))

