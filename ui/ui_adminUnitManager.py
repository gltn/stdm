# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_adminUnitManager.ui'
#
# Created: Fri Mar 07 12:28:30 2014
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

class Ui_frmAdminUnitManager(object):
    def setupUi(self, frmAdminUnitManager):
        frmAdminUnitManager.setObjectName(_fromUtf8("frmAdminUnitManager"))
        frmAdminUnitManager.resize(369, 407)
        self.gridLayout = QtGui.QGridLayout(frmAdminUnitManager)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)
        self.tvAdminUnits = QtGui.QTreeView(frmAdminUnitManager)
        self.tvAdminUnits.setObjectName(_fromUtf8("tvAdminUnits"))
        self.gridLayout.addWidget(self.tvAdminUnits, 1, 0, 1, 2)
        self.btnRemove = QtGui.QPushButton(frmAdminUnitManager)
        self.btnRemove.setMinimumSize(QtCore.QSize(0, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/remove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRemove.setIcon(icon)
        self.btnRemove.setObjectName(_fromUtf8("btnRemove"))
        self.gridLayout.addWidget(self.btnRemove, 2, 0, 1, 1)
        self.btnClear = QtGui.QPushButton(frmAdminUnitManager)
        self.btnClear.setMinimumSize(QtCore.QSize(0, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/reset.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnClear.setIcon(icon1)
        self.btnClear.setObjectName(_fromUtf8("btnClear"))
        self.gridLayout.addWidget(self.btnClear, 2, 1, 1, 1)
        self.gbManage = QtGui.QGroupBox(frmAdminUnitManager)
        self.gbManage.setFlat(False)
        self.gbManage.setObjectName(_fromUtf8("gbManage"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.gbManage)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.gbManage)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.txtUnitName = ValidatingLineEdit(self.gbManage)
        self.txtUnitName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtUnitName.setMaxLength(50)
        self.txtUnitName.setObjectName(_fromUtf8("txtUnitName"))
        self.horizontalLayout.addWidget(self.txtUnitName)
        self.label_2 = QtGui.QLabel(self.gbManage)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.txtUnitCode = ValidatingLineEdit(self.gbManage)
        self.txtUnitCode.setMinimumSize(QtCore.QSize(0, 30))
        self.txtUnitCode.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txtUnitCode.setMaxLength(10)
        self.txtUnitCode.setObjectName(_fromUtf8("txtUnitCode"))
        self.horizontalLayout.addWidget(self.txtUnitCode)
        self.btnAdd = QtGui.QPushButton(self.gbManage)
        self.btnAdd.setMinimumSize(QtCore.QSize(30, 30))
        self.btnAdd.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAdd.setIcon(icon2)
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.horizontalLayout.addWidget(self.btnAdd)
        self.gridLayout.addWidget(self.gbManage, 3, 0, 1, 2)

        self.retranslateUi(frmAdminUnitManager)
        QtCore.QMetaObject.connectSlotsByName(frmAdminUnitManager)

    def retranslateUi(self, frmAdminUnitManager):
        frmAdminUnitManager.setWindowTitle(_translate("frmAdminUnitManager", "Administrative Unit Manager", None))
        self.btnRemove.setText(_translate("frmAdminUnitManager", "Delete Selection", None))
        self.btnClear.setText(_translate("frmAdminUnitManager", "Clear Selection", None))
        self.gbManage.setTitle(_translate("frmAdminUnitManager", "New Administrative Unit:", None))
        self.label.setText(_translate("frmAdminUnitManager", "Unit Name", None))
        self.label_2.setText(_translate("frmAdminUnitManager", "Code", None))

from customcontrols import ValidatingLineEdit
