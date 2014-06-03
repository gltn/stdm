# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_survey.ui'
#
# Created: Wed Mar 19 11:15:10 2014
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

class Ui_frmSurvey(object):
    def setupUi(self, frmSurvey):
        frmSurvey.setObjectName(_fromUtf8("frmSurvey"))
        frmSurvey.resize(424, 364)
        self.gridLayout = QtGui.QGridLayout(frmSurvey)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(frmSurvey)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtSurveyCode = QtGui.QLineEdit(frmSurvey)
        self.txtSurveyCode.setMinimumSize(QtCore.QSize(0, 30))
        self.txtSurveyCode.setReadOnly(True)
        self.txtSurveyCode.setObjectName(_fromUtf8("txtSurveyCode"))
        self.gridLayout.addWidget(self.txtSurveyCode, 1, 1, 1, 1)
        self.label = QtGui.QLabel(frmSurvey)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.dtEnumDate = QtGui.QDateEdit(frmSurvey)
        self.dtEnumDate.setMinimumSize(QtCore.QSize(0, 30))
        self.dtEnumDate.setCalendarPopup(True)
        self.dtEnumDate.setObjectName(_fromUtf8("dtEnumDate"))
        self.gridLayout.addWidget(self.dtEnumDate, 2, 1, 1, 1)
        self.tabWidget = QtGui.QTabWidget(frmSurvey)
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
        self.gridLayout.addWidget(self.tabWidget, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(frmSurvey)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)

        self.retranslateUi(frmSurvey)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmSurvey)

    def retranslateUi(self, frmSurvey):
        frmSurvey.setWindowTitle(_translate("frmSurvey", "Survey Details", None))
        self.label_2.setText(_translate("frmSurvey", "Survey Code", None))
        self.label.setText(_translate("frmSurvey", "Enumeration Date", None))
        self.dtEnumDate.setDisplayFormat(_translate("frmSurvey", "dd/MM/yyyy", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("frmSurvey", "Enumerator", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("frmSurvey", "Respondent", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("frmSurvey", "Witnesses", None))

from .foreign_key_mapper import ForeignKeyMapper
