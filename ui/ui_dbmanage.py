# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dbmanage.ui'
#
# Created: Fri Jun 07 12:06:54 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmEntityManage(object):
    def setupUi(self, frmEntityManage):
        frmEntityManage.setObjectName(_fromUtf8("frmEntityManage"))
        frmEntityManage.resize(698, 592)
        self.gridLayout = QtGui.QGridLayout(frmEntityManage)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.entityStackCnt = QtGui.QStackedWidget(frmEntityManage)
        self.entityStackCnt.setFrameShape(QtGui.QFrame.Box)
        self.entityStackCnt.setLineWidth(0)
        self.entityStackCnt.setObjectName(_fromUtf8("entityStackCnt"))
        self.gridLayout.addWidget(self.entityStackCnt, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmEntityManage)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)
        self.stdmEntities = QtGui.QListWidget(frmEntityManage)
        self.stdmEntities.setMaximumSize(QtCore.QSize(105, 16777215))
        self.stdmEntities.setMidLineWidth(0)
        self.stdmEntities.setIconSize(QtCore.QSize(64, 64))
        self.stdmEntities.setTextElideMode(QtCore.Qt.ElideLeft)
        self.stdmEntities.setMovement(QtGui.QListView.Static)
        self.stdmEntities.setFlow(QtGui.QListView.TopToBottom)
        self.stdmEntities.setProperty("isWrapping", True)
        self.stdmEntities.setResizeMode(QtGui.QListView.Adjust)
        self.stdmEntities.setLayoutMode(QtGui.QListView.Batched)
        self.stdmEntities.setSpacing(5)
        self.stdmEntities.setViewMode(QtGui.QListView.IconMode)
        self.stdmEntities.setSelectionRectVisible(False)
        self.stdmEntities.setObjectName(_fromUtf8("stdmEntities"))
        self.gridLayout.addWidget(self.stdmEntities, 0, 0, 1, 1)

        self.retranslateUi(frmEntityManage)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), frmEntityManage.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmEntityManage.reject)
        QtCore.QMetaObject.connectSlotsByName(frmEntityManage)

    def retranslateUi(self, frmEntityManage):
        frmEntityManage.setWindowTitle(QtGui.QApplication.translate("frmEntityManage", "STDM Entity Management", None, QtGui.QApplication.UnicodeUTF8))

