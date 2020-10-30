# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_str_view_entity.ui'
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

class Ui_frmSTRViewEntity(object):
    def setupUi(self, frmSTRViewEntity):
        frmSTRViewEntity.setObjectName(_fromUtf8("frmSTRViewEntity"))
        frmSTRViewEntity.resize(293, 172)
        self.gridLayout = QtGui.QGridLayout(frmSTRViewEntity)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tbSTRViewEntity = QtGui.QTabWidget(frmSTRViewEntity)
        self.tbSTRViewEntity.setTabPosition(QtGui.QTabWidget.South)
        self.tbSTRViewEntity.setDocumentMode(False)
        self.tbSTRViewEntity.setTabsClosable(False)
        self.tbSTRViewEntity.setMovable(False)
        self.tbSTRViewEntity.setObjectName(_fromUtf8("tbSTRViewEntity"))
        self.filter = QtGui.QWidget()
        self.filter.setObjectName(_fromUtf8("filter"))
        self.gridLayout_2 = QtGui.QGridLayout(self.filter)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.filter)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 2)
        self.txtFilterPattern = QtGui.QLineEdit(self.filter)
        self.txtFilterPattern.setMinimumSize(QtCore.QSize(0, 30))
        self.txtFilterPattern.setObjectName(_fromUtf8("txtFilterPattern"))
        self.gridLayout_2.addWidget(self.txtFilterPattern, 0, 0, 1, 2)
        self.cboFilterCol = QtGui.QComboBox(self.filter)
        self.cboFilterCol.setMinimumSize(QtCore.QSize(0, 30))
        self.cboFilterCol.setObjectName(_fromUtf8("cboFilterCol"))
        self.gridLayout_2.addWidget(self.cboFilterCol, 2, 0, 1, 2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/filter.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tbSTRViewEntity.addTab(self.filter, icon, _fromUtf8(""))
        self.validity = QtGui.QWidget()
        self.validity.setObjectName(_fromUtf8("validity"))
        self.verticalLayout = QtGui.QVBoxLayout(self.validity)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(self.validity)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.validity_from_date = QtGui.QDateEdit(self.validity)
        self.validity_from_date.setCalendarPopup(True)
        self.validity_from_date.setObjectName(_fromUtf8("validity_from_date"))
        self.horizontalLayout.addWidget(self.validity_from_date)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lable_3 = QtGui.QLabel(self.validity)
        self.lable_3.setObjectName(_fromUtf8("lable_3"))
        self.horizontalLayout_2.addWidget(self.lable_3)
        self.validity_to_date = QtGui.QDateEdit(self.validity)
        self.validity_to_date.setCalendarPopup(True)
        self.validity_to_date.setObjectName(_fromUtf8("validity_to_date"))
        self.horizontalLayout_2.addWidget(self.validity_to_date)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/period_blue.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tbSTRViewEntity.addTab(self.validity, icon1, _fromUtf8(""))
        self.gridLayout.addWidget(self.tbSTRViewEntity, 0, 0, 1, 1)

        self.retranslateUi(frmSTRViewEntity)
        self.tbSTRViewEntity.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmSTRViewEntity)

    def retranslateUi(self, frmSTRViewEntity):
        frmSTRViewEntity.setWindowTitle(_translate("frmSTRViewEntity", "Form", None))
        self.label.setText(_translate("frmSTRViewEntity", "in column", None))
        self.txtFilterPattern.setPlaceholderText(_translate("frmSTRViewEntity", "Look for", None))
        self.tbSTRViewEntity.setTabText(self.tbSTRViewEntity.indexOf(self.filter), _translate("frmSTRViewEntity", "Filter", None))
        self.label_2.setText(_translate("frmSTRViewEntity", "Validity from", None))
        self.lable_3.setText(_translate("frmSTRViewEntity", "to", None))
        self.tbSTRViewEntity.setTabText(self.tbSTRViewEntity.indexOf(self.validity), _translate("frmSTRViewEntity", "Validity Period", None))

