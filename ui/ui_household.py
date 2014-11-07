# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_household.ui'
#
# Created: Mon Mar 24 13:29:12 2014
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

class Ui_frmHousehold(object):
    def setupUi(self, frmHousehold):
        frmHousehold.setObjectName(_fromUtf8("frmHousehold"))
        frmHousehold.resize(352, 336)
        self.gridLayout = QtGui.QGridLayout(frmHousehold)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)
        self.label_7 = QtGui.QLabel(frmHousehold)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.sbFemaleNumber = QtGui.QSpinBox(frmHousehold)
        self.sbFemaleNumber.setMinimumSize(QtCore.QSize(0, 30))
        self.sbFemaleNumber.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.sbFemaleNumber.setObjectName(_fromUtf8("sbFemaleNumber"))
        self.gridLayout.addWidget(self.sbFemaleNumber, 1, 1, 1, 1)
        self.label_8 = QtGui.QLabel(frmHousehold)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.sbMaleNumber = QtGui.QSpinBox(frmHousehold)
        self.sbMaleNumber.setMinimumSize(QtCore.QSize(0, 30))
        self.sbMaleNumber.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.sbMaleNumber.setPrefix(_fromUtf8(""))
        self.sbMaleNumber.setMaximum(99)
        self.sbMaleNumber.setObjectName(_fromUtf8("sbMaleNumber"))
        self.gridLayout.addWidget(self.sbMaleNumber, 2, 1, 1, 1)
        self.label_9 = QtGui.QLabel(frmHousehold)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 3, 0, 1, 1)
        self.sbMonthlyIncome = QtGui.QSpinBox(frmHousehold)
        self.sbMonthlyIncome.setMinimumSize(QtCore.QSize(0, 30))
        self.sbMonthlyIncome.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.sbMonthlyIncome.setMaximum(1000000000)
        self.sbMonthlyIncome.setObjectName(_fromUtf8("sbMonthlyIncome"))
        self.gridLayout.addWidget(self.sbMonthlyIncome, 3, 1, 1, 1)
        self.tabWidget = QtGui.QTabWidget(frmHousehold)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = ForeignKeyMapper()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = ForeignKeyMapper()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 4, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(frmHousehold)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)

        self.retranslateUi(frmHousehold)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), frmHousehold.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmHousehold.reject)
        QtCore.QMetaObject.connectSlotsByName(frmHousehold)

    def retranslateUi(self, frmHousehold):
        frmHousehold.setWindowTitle(_translate("frmHousehold", "Household Details", None))
        self.label_7.setText(_translate("frmHousehold", "Number of Females", None))
        self.label_8.setText(_translate("frmHousehold", "Number of Males", None))
        self.label_9.setText(_translate("frmHousehold", "Total Monthly Income", None))
        self.sbMonthlyIncome.setPrefix(_translate("frmHousehold", "UGSHS", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("frmHousehold", "Income Sources", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("frmHousehold", "Savings", None))

from .foreign_key_mapper import ForeignKeyMapper
