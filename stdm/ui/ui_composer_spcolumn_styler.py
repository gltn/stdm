# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_spcolumn_styler.ui'
#
# Created: Sun May 25 20:41:51 2014
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


class Ui_frmComposerSpatialColumnEditor(object):
    def setupUi(self, frmComposerSpatialColumnEditor):
        frmComposerSpatialColumnEditor.setObjectName(_fromUtf8("frmComposerSpatialColumnEditor"))
        frmComposerSpatialColumnEditor.resize(334, 320)
        self.gridLayout = QtGui.QGridLayout(frmComposerSpatialColumnEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(frmComposerSpatialColumnEditor)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.style = QtGui.QWidget()
        self.style.setObjectName(_fromUtf8("style"))
        self.gridLayout_3 = QtGui.QGridLayout(self.style)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.styleScrollArea = QtGui.QScrollArea(self.style)
        self.styleScrollArea.setWidgetResizable(True)
        self.styleScrollArea.setObjectName(_fromUtf8("styleScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 290, 257))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_5 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.styleLayout = QtGui.QGridLayout()
        self.styleLayout.setObjectName(_fromUtf8("styleLayout"))
        self.gridLayout_5.addLayout(self.styleLayout, 0, 0, 1, 1)
        self.styleScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.styleScrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.style, _fromUtf8(""))
        self.label = QtGui.QWidget()
        self.label.setObjectName(_fromUtf8("label"))
        self.labelLayout = QtGui.QVBoxLayout(self.label)
        self.labelLayout.setSpacing(10)
        self.labelLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.labelLayout.setContentsMargins(-1, -1, -1, 9)
        self.labelLayout.setObjectName(_fromUtf8("labelLayout"))
        self.label_2 = QtGui.QLabel(self.label)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.labelLayout.addWidget(self.label_2)
        self.cboLabelField = QtGui.QComboBox(self.label)
        self.cboLabelField.setMinimumSize(QtCore.QSize(0, 30))
        self.cboLabelField.setObjectName(_fromUtf8("cboLabelField"))
        self.labelLayout.addWidget(self.cboLabelField)
        self.tabWidget.addTab(self.label, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(frmComposerSpatialColumnEditor)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmComposerSpatialColumnEditor)

    def retranslateUi(self, frmComposerSpatialColumnEditor):
        frmComposerSpatialColumnEditor.setWindowTitle(
            _translate("frmComposerSpatialColumnEditor", "Spatial Column Style Editor", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.style),
                                  _translate("frmComposerSpatialColumnEditor", "Style", None))
        self.label_2.setText(_translate("frmComposerSpatialColumnEditor",
                                        "<html><head/><body><p>Select the field whose value will be used to label the feature</p></body></html>",
                                        None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.label),
                                  _translate("frmComposerSpatialColumnEditor", "Label", None))
