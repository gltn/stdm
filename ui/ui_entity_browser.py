# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_entity_browser.ui'
#
# Created: Sun Jul 31 09:45:28 2016
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EntityBrowser(object):
    def setupUi(self, EntityBrowser):
        EntityBrowser.setObjectName(_fromUtf8("EntityBrowser"))
        EntityBrowser.resize(650, 416)
        self.gridLayout = QtGui.QGridLayout(EntityBrowser)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(EntityBrowser)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EntityBrowser)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.label_2 = QtGui.QLabel(EntityBrowser)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 2, 1, 1)
        self.cboFilterColumn = QtGui.QComboBox(EntityBrowser)
        self.cboFilterColumn.setMinimumSize(QtCore.QSize(150, 30))
        self.cboFilterColumn.setObjectName(_fromUtf8("cboFilterColumn"))
        self.gridLayout.addWidget(self.cboFilterColumn, 3, 3, 1, 1)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 4)
        self.tbEntity = QtGui.QTableView(EntityBrowser)
        self.tbEntity.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tbEntity.setAlternatingRowColors(True)
        self.tbEntity.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tbEntity.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tbEntity.setObjectName(_fromUtf8("tbEntity"))
        self.gridLayout.addWidget(self.tbEntity, 2, 0, 1, 4)
        self.txtFilterPattern = QtGui.QLineEdit(EntityBrowser)
        self.txtFilterPattern.setMinimumSize(QtCore.QSize(0, 30))
        self.txtFilterPattern.setMaxLength(50)
        self.txtFilterPattern.setObjectName(_fromUtf8("txtFilterPattern"))
        self.gridLayout.addWidget(self.txtFilterPattern, 3, 1, 1, 1)
        self.vlActions = QtGui.QVBoxLayout()
        self.vlActions.setObjectName(_fromUtf8("vlActions"))
        self.gridLayout.addLayout(self.vlActions, 1, 0, 1, 4)

        self.retranslateUi(EntityBrowser)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EntityBrowser.reject)
        QtCore.QMetaObject.connectSlotsByName(EntityBrowser)

    def retranslateUi(self, EntityBrowser):
        EntityBrowser.setWindowTitle(QtGui.QApplication.translate("EntityBrowser", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EntityBrowser", "Look For", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("EntityBrowser", "In Column", None, QtGui.QApplication.UnicodeUTF8))
        self.txtFilterPattern.setPlaceholderText(QtGui.QApplication.translate("EntityBrowser", "Type the filter keyword here...", None, QtGui.QApplication.UnicodeUTF8))

