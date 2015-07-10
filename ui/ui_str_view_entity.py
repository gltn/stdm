# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_str_view_entity.ui'
#
# Created: Fri Oct 17 08:54:19 2014
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

class Ui_frmSTRViewEntity(object):
    def setupUi(self, frmSTRViewEntity):
        frmSTRViewEntity.setObjectName(_fromUtf8("frmSTRViewEntity"))
        frmSTRViewEntity.resize(293, 172)
        self.gridLayout = QtGui.QGridLayout(frmSTRViewEntity)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tbSTRViewEntity = QtGui.QTabWidget(frmSTRViewEntity)
        self.tbSTRViewEntity.setTabPosition(QtGui.QTabWidget.South)
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
        self.gridLayout.addWidget(self.tbSTRViewEntity, 0, 0, 1, 1)

        self.retranslateUi(frmSTRViewEntity)
        self.tbSTRViewEntity.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmSTRViewEntity)

    def retranslateUi(self, frmSTRViewEntity):
        frmSTRViewEntity.setWindowTitle(_translate("frmSTRViewEntity", "Form", None))
        self.label.setText(_translate("frmSTRViewEntity", "in column", None))
        self.txtFilterPattern.setPlaceholderText(_translate("frmSTRViewEntity", "Look for", None))
        self.tbSTRViewEntity.setTabText(self.tbSTRViewEntity.indexOf(self.filter), _translate("frmSTRViewEntity", "Filter", None))
