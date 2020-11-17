# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_composer_data_source.ui'
#
# Created: Sun May 18 19:18:13 2014
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


class Ui_frmComposerDataSource(object):
    def setupUi(self, frmComposerDataSource):
        frmComposerDataSource.setObjectName(_fromUtf8("frmComposerDataSource"))
        frmComposerDataSource.resize(380, 130)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmComposerDataSource.sizePolicy().hasHeightForWidth())
        frmComposerDataSource.setSizePolicy(sizePolicy)
        frmComposerDataSource.setMaximumSize(QtCore.QSize(16777215, 130))
        self.gridLayout = QtGui.QGridLayout(frmComposerDataSource)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(frmComposerDataSource)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setStyleSheet(_fromUtf8("padding: 2px; font-weight: bold; background-color: rgb(200, 200, 200);"))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.label_2 = QtGui.QLabel(frmComposerDataSource)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 100))
        self.label_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)
        self.cboDataSource = QtGui.QComboBox(frmComposerDataSource)
        self.cboDataSource.setMinimumSize(QtCore.QSize(0, 30))
        self.cboDataSource.setObjectName(_fromUtf8("cboDataSource"))
        self.gridLayout.addWidget(self.cboDataSource, 2, 0, 1, 2)
        self.rbTables = QtGui.QRadioButton(frmComposerDataSource)
        self.rbTables.setObjectName(_fromUtf8("rbTables"))
        self.gridLayout.addWidget(self.rbTables, 3, 0, 1, 1)
        self.rbViews = QtGui.QRadioButton(frmComposerDataSource)
        self.rbViews.setObjectName(_fromUtf8("rbViews"))
        self.gridLayout.addWidget(self.rbViews, 3, 1, 1, 1)

        self.retranslateUi(frmComposerDataSource)
        QtCore.QMetaObject.connectSlotsByName(frmComposerDataSource)

    def retranslateUi(self, frmComposerDataSource):
        frmComposerDataSource.setWindowTitle(_translate("frmComposerDataSource", "Data Source", None))
        self.label.setText(_translate("frmComposerDataSource", "Data Source", None))
        self.label_2.setText(_translate("frmComposerDataSource",
                                        "<html><head/><body><p>Please select the name of the source table or view from the options below</p></body></html>",
                                        None))
        self.rbTables.setText(_translate("frmComposerDataSource", "Show tables only", None))
        self.rbViews.setText(_translate("frmComposerDataSource", "Show views only", None))
