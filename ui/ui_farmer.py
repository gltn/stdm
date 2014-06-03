# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_farmer.ui'
#
# Created: Sat Mar 22 11:08:40 2014
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

class Ui_frmFarmer(object):
    def setupUi(self, frmFarmer):
        frmFarmer.setObjectName(_fromUtf8("frmFarmer"))
        frmFarmer.resize(415, 561)
        self.gridLayout = QtGui.QGridLayout(frmFarmer)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)
        self.label = QtGui.QLabel(frmFarmer)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.txtFirstName = QtGui.QLineEdit(frmFarmer)
        self.txtFirstName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtFirstName.setMaxLength(50)
        self.txtFirstName.setObjectName(_fromUtf8("txtFirstName"))
        self.gridLayout.addWidget(self.txtFirstName, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(frmFarmer)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.txtLastName = QtGui.QLineEdit(frmFarmer)
        self.txtLastName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtLastName.setMaxLength(50)
        self.txtLastName.setObjectName(_fromUtf8("txtLastName"))
        self.gridLayout.addWidget(self.txtLastName, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(frmFarmer)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.cboGender = QtGui.QComboBox(frmFarmer)
        self.cboGender.setMinimumSize(QtCore.QSize(0, 30))
        self.cboGender.setObjectName(_fromUtf8("cboGender"))
        self.gridLayout.addWidget(self.cboGender, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(frmFarmer)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.dtDoB = QtGui.QDateEdit(frmFarmer)
        self.dtDoB.setMinimumSize(QtCore.QSize(0, 30))
        self.dtDoB.setCalendarPopup(True)
        self.dtDoB.setObjectName(_fromUtf8("dtDoB"))
        self.gridLayout.addWidget(self.dtDoB, 4, 1, 1, 1)
        self.label_5 = QtGui.QLabel(frmFarmer)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.cboMaritalStatus = QtGui.QComboBox(frmFarmer)
        self.cboMaritalStatus.setMinimumSize(QtCore.QSize(0, 30))
        self.cboMaritalStatus.setObjectName(_fromUtf8("cboMaritalStatus"))
        self.gridLayout.addWidget(self.cboMaritalStatus, 5, 1, 1, 1)
        self.label_6 = QtGui.QLabel(frmFarmer)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.txtCellphone = QtGui.QLineEdit(frmFarmer)
        self.txtCellphone.setMinimumSize(QtCore.QSize(0, 30))
        self.txtCellphone.setMaxLength(20)
        self.txtCellphone.setObjectName(_fromUtf8("txtCellphone"))
        self.gridLayout.addWidget(self.txtCellphone, 6, 1, 1, 1)
        self.label_7 = QtGui.QLabel(frmFarmer)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 7, 0, 1, 1)
        self.txtFarmerNumber = ValidatingLineEdit(frmFarmer)
        self.txtFarmerNumber.setMinimumSize(QtCore.QSize(0, 30))
        self.txtFarmerNumber.setObjectName(_fromUtf8("txtFarmerNumber"))
        self.gridLayout.addWidget(self.txtFarmerNumber, 7, 1, 1, 1)
        self.tabWidget = QtGui.QTabWidget(frmFarmer)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = ForeignKeyMapper()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = ForeignKeyMapper()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = ForeignKeyMapper()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 8, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(frmFarmer)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)

        self.retranslateUi(frmFarmer)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmFarmer)
        frmFarmer.setTabOrder(self.txtFirstName, self.txtLastName)
        frmFarmer.setTabOrder(self.txtLastName, self.cboGender)
        frmFarmer.setTabOrder(self.cboGender, self.dtDoB)
        frmFarmer.setTabOrder(self.dtDoB, self.cboMaritalStatus)
        frmFarmer.setTabOrder(self.cboMaritalStatus, self.txtCellphone)
        frmFarmer.setTabOrder(self.txtCellphone, self.buttonBox)

    def retranslateUi(self, frmFarmer):
        frmFarmer.setWindowTitle(_translate("frmFarmer", "Farmer Editor", None))
        self.label.setText(_translate("frmFarmer", "First Name", None))
        self.label_2.setText(_translate("frmFarmer", "Last Name", None))
        self.label_3.setText(_translate("frmFarmer", "Gender", None))
        self.label_4.setText(_translate("frmFarmer", "Date of Birth", None))
        self.dtDoB.setDisplayFormat(_translate("frmFarmer", "dd/MM/yyyy", None))
        self.label_5.setText(_translate("frmFarmer", "Marital Status", None))
        self.label_6.setText(_translate("frmFarmer", "Cellphone", None))
        self.label_7.setText(_translate("frmFarmer", "Farmer Number", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("frmFarmer", "Household", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("frmFarmer", "Priority Services", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("frmFarmer", "Impacts", None))

from customcontrols import ValidatingLineEdit
from .foreign_key_mapper import ForeignKeyMapper
