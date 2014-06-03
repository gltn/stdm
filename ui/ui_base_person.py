# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_base_person.ui'
#
# Created: Tue Mar 18 15:58:59 2014
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

class Ui_frmBasePerson(object):
    def setupUi(self, frmBasePerson):
        frmBasePerson.setObjectName(_fromUtf8("frmBasePerson"))
        frmBasePerson.resize(325, 377)
        self.gridLayout = QtGui.QGridLayout(frmBasePerson)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtLastName = QtGui.QLineEdit(frmBasePerson)
        self.txtLastName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtLastName.setMaxLength(50)
        self.txtLastName.setObjectName(_fromUtf8("txtLastName"))
        self.gridLayout.addWidget(self.txtLastName, 3, 1, 1, 1)
        self.label_6 = QtGui.QLabel(frmBasePerson)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 7, 0, 1, 1)
        self.txtCellphone = QtGui.QLineEdit(frmBasePerson)
        self.txtCellphone.setMinimumSize(QtCore.QSize(0, 30))
        self.txtCellphone.setMaxLength(20)
        self.txtCellphone.setObjectName(_fromUtf8("txtCellphone"))
        self.gridLayout.addWidget(self.txtCellphone, 7, 1, 1, 1)
        self.dtDoB = QtGui.QDateEdit(frmBasePerson)
        self.dtDoB.setMinimumSize(QtCore.QSize(0, 30))
        self.dtDoB.setCalendarPopup(True)
        self.dtDoB.setObjectName(_fromUtf8("dtDoB"))
        self.gridLayout.addWidget(self.dtDoB, 5, 1, 1, 1)
        self.txtFirstName = QtGui.QLineEdit(frmBasePerson)
        self.txtFirstName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtFirstName.setMaxLength(50)
        self.txtFirstName.setObjectName(_fromUtf8("txtFirstName"))
        self.gridLayout.addWidget(self.txtFirstName, 2, 1, 1, 1)
        self.label = QtGui.QLabel(frmBasePerson)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(frmBasePerson)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.cboGender = QtGui.QComboBox(frmBasePerson)
        self.cboGender.setMinimumSize(QtCore.QSize(0, 30))
        self.cboGender.setObjectName(_fromUtf8("cboGender"))
        self.gridLayout.addWidget(self.cboGender, 4, 1, 1, 1)
        self.label_5 = QtGui.QLabel(frmBasePerson)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 6, 0, 1, 1)
        self.label_4 = QtGui.QLabel(frmBasePerson)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.cboMaritalStatus = QtGui.QComboBox(frmBasePerson)
        self.cboMaritalStatus.setMinimumSize(QtCore.QSize(0, 30))
        self.cboMaritalStatus.setObjectName(_fromUtf8("cboMaritalStatus"))
        self.gridLayout.addWidget(self.cboMaritalStatus, 6, 1, 1, 1)
        self.label_2 = QtGui.QLabel(frmBasePerson)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmBasePerson)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 1, 0, 1, 2)

        self.retranslateUi(frmBasePerson)
        QtCore.QMetaObject.connectSlotsByName(frmBasePerson)
        frmBasePerson.setTabOrder(self.txtFirstName, self.txtLastName)
        frmBasePerson.setTabOrder(self.txtLastName, self.cboGender)
        frmBasePerson.setTabOrder(self.cboGender, self.dtDoB)
        frmBasePerson.setTabOrder(self.dtDoB, self.cboMaritalStatus)
        frmBasePerson.setTabOrder(self.cboMaritalStatus, self.txtCellphone)
        frmBasePerson.setTabOrder(self.txtCellphone, self.buttonBox)

    def retranslateUi(self, frmBasePerson):
        frmBasePerson.setWindowTitle(_translate("frmBasePerson", "Base Person", None))
        self.label_6.setText(_translate("frmBasePerson", "Cellphone", None))
        self.dtDoB.setDisplayFormat(_translate("frmBasePerson", "dd/MM/yyyy", None))
        self.label.setText(_translate("frmBasePerson", "First Name", None))
        self.label_3.setText(_translate("frmBasePerson", "Gender", None))
        self.label_5.setText(_translate("frmBasePerson", "Marital Status", None))
        self.label_4.setText(_translate("frmBasePerson", "Date of Birth", None))
        self.label_2.setText(_translate("frmBasePerson", "Last Name", None))

