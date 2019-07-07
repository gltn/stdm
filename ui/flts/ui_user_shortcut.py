# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_user_shortcut.ui'
#
# Created: Sat Jul  6 14:53:55 2019
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_UserShortcutDialog(object):
    def setupUi(self, UserShortcutDialog):
        UserShortcutDialog.setObjectName(_fromUtf8("UserShortcutDialog"))
        UserShortcutDialog.resize(822, 479)
        self.gridLayout = QtGui.QGridLayout(UserShortcutDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chb_donotshow = QtGui.QCheckBox(UserShortcutDialog)
        self.chb_donotshow.setObjectName(_fromUtf8("chb_donotshow"))
        self.gridLayout.addWidget(self.chb_donotshow, 3, 0, 1, 1)
        self.label = QtGui.QLabel(UserShortcutDialog)
        self.label.setMaximumSize(QtCore.QSize(16777215, 30))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(UserShortcutDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 1)
        self.splitter = QtGui.QSplitter(UserShortcutDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tr_title_category = QtGui.QTreeWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tr_title_category.sizePolicy().hasHeightForWidth())
        self.tr_title_category.setSizePolicy(sizePolicy)
        self.tr_title_category.setMinimumSize(QtCore.QSize(149, 0))
        self.tr_title_category.setMaximumSize(QtCore.QSize(300, 16777215))
        self.tr_title_category.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tr_title_category.setObjectName(_fromUtf8("tr_title_category"))
        self.tr_title_category.headerItem().setText(0, _fromUtf8("1"))
        self.tr_title_category.header().setVisible(False)
        self.lsw_category_action = QtGui.QListWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lsw_category_action.sizePolicy().hasHeightForWidth())
        self.lsw_category_action.setSizePolicy(sizePolicy)
        self.lsw_category_action.setMinimumSize(QtCore.QSize(300, 0))
        self.lsw_category_action.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lsw_category_action.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.lsw_category_action.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.lsw_category_action.setIconSize(QtCore.QSize(36, 36))
        self.lsw_category_action.setTextElideMode(QtCore.Qt.ElideNone)
        self.lsw_category_action.setMovement(QtGui.QListView.Static)
        self.lsw_category_action.setProperty("isWrapping", True)
        self.lsw_category_action.setResizeMode(QtGui.QListView.Fixed)
        self.lsw_category_action.setLayoutMode(QtGui.QListView.Batched)
        self.lsw_category_action.setGridSize(QtCore.QSize(84, 84))
        self.lsw_category_action.setViewMode(QtGui.QListView.IconMode)
        self.lsw_category_action.setModelColumn(0)
        self.lsw_category_action.setUniformItemSizes(False)
        self.lsw_category_action.setWordWrap(True)
        self.lsw_category_action.setObjectName(_fromUtf8("lsw_category_action"))
        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 1)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 1)

        self.retranslateUi(UserShortcutDialog)
        self.lsw_category_action.setCurrentRow(-1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UserShortcutDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UserShortcutDialog)

    def retranslateUi(self, UserShortcutDialog):
        UserShortcutDialog.setWindowTitle(_translate("UserShortcutDialog", "Flexible Land Tenure System", None))
        self.chb_donotshow.setText(_translate("UserShortcutDialog", "Do not show this dialog again on login", None))
        self.label.setText(_translate("UserShortcutDialog", "<html><head/><body><p>Please select an action to perform</p></body></html>", None))
        self.lsw_category_action.setSortingEnabled(False)

