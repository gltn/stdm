# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/Junk/Test/ui_scheme_manager.ui'
#
# Created: Thu Aug 08 00:45:06 2019
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_SchemeManagerDlg(object):
    def setupUi(self, SchemeManagerDlg):
        SchemeManagerDlg.setObjectName(_fromUtf8("SchemeManagerDlg"))
        SchemeManagerDlg.resize(866, 631)
        SchemeManagerDlg.setModal(False)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(SchemeManagerDlg)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.splitter = QtGui.QSplitter(SchemeManagerDlg)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 8)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.approveButton = QtGui.QPushButton(self.widget)
        self.approveButton.setObjectName(_fromUtf8("approveButton"))
        self.horizontalLayout.addWidget(self.approveButton)
        self.disapproveButton = QtGui.QPushButton(self.widget)
        self.disapproveButton.setObjectName(_fromUtf8("disapproveButton"))
        self.horizontalLayout.addWidget(self.disapproveButton)
        self.saveButton = QtGui.QPushButton(self.widget)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.horizontalLayout.addWidget(self.saveButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.searchLineEdit = QtGui.QLineEdit(self.widget)
        self.searchLineEdit.setObjectName(_fromUtf8("searchLineEdit"))
        self.horizontalLayout.addWidget(self.searchLineEdit)
        self.searchComboBox = QtGui.QComboBox(self.widget)
        self.searchComboBox.setObjectName(_fromUtf8("searchComboBox"))
        self.searchComboBox.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.searchComboBox)
        self.searchButton = QtGui.QPushButton(self.widget)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.horizontalLayout.addWidget(self.searchButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 15, -1, -1)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.schemeTableView = QtGui.QTableView(self.widget)
        self.schemeTableView.setObjectName(_fromUtf8("schemeTableView"))
        self.verticalLayout.addWidget(self.schemeTableView)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.firstButton = QtGui.QPushButton(self.widget)
        self.firstButton.setObjectName(_fromUtf8("firstButton"))
        self.horizontalLayout_2.addWidget(self.firstButton)
        self.previousButton = QtGui.QPushButton(self.widget)
        self.previousButton.setObjectName(_fromUtf8("previousButton"))
        self.horizontalLayout_2.addWidget(self.previousButton)
        self.recordLineEdit = QtGui.QLineEdit(self.widget)
        self.recordLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.recordLineEdit.setObjectName(_fromUtf8("recordLineEdit"))
        self.horizontalLayout_2.addWidget(self.recordLineEdit)
        self.nextButton = QtGui.QPushButton(self.widget)
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.horizontalLayout_2.addWidget(self.nextButton)
        self.lastButton = QtGui.QPushButton(self.widget)
        self.lastButton.setObjectName(_fromUtf8("lastButton"))
        self.horizontalLayout_2.addWidget(self.lastButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.widget1 = QtGui.QWidget(self.splitter)
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget1)
        self.verticalLayout_4.setContentsMargins(-1, 8, -1, -1)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_2 = QtGui.QLabel(self.widget1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_4.addWidget(self.label_2)
        self.tabWidget = QtGui.QTabWidget(self.widget1)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.verticalLayout_4.addWidget(self.tabWidget)
        self.horizontalLayout_3.addWidget(self.splitter)

        self.retranslateUi(SchemeManagerDlg)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SchemeManagerDlg)

    def retranslateUi(self, SchemeManagerDlg):
        SchemeManagerDlg.setWindowTitle(_translate("SchemeManagerDlg", "Scheme Manager", None))
        self.approveButton.setText(_translate("SchemeManagerDlg", "Approve", None))
        self.disapproveButton.setText(_translate("SchemeManagerDlg", "Disapprove", None))
        self.saveButton.setText(_translate("SchemeManagerDlg", "Save", None))
        self.searchLineEdit.setPlaceholderText(_translate("SchemeManagerDlg", "Type to search...", None))
        self.searchComboBox.setItemText(0, _translate("SchemeManagerDlg", "Apply Filter", None))
        self.searchButton.setText(_translate("SchemeManagerDlg", "Search", None))
        self.label.setText(_translate("SchemeManagerDlg", "<html><head/><body><p><span style=\" font-weight:600;\">All Schemes:</span></p></body></html>", None))
        self.firstButton.setText(_translate("SchemeManagerDlg", "First", None))
        self.previousButton.setText(_translate("SchemeManagerDlg", "Previous", None))
        self.recordLineEdit.setText(_translate("SchemeManagerDlg", "Record 0 of 0 records", None))
        self.nextButton.setText(_translate("SchemeManagerDlg", "Next", None))
        self.lastButton.setText(_translate("SchemeManagerDlg", "Last", None))
        self.label_2.setText(_translate("SchemeManagerDlg", "<html><head/><body><p><span style=\" font-weight:600;\">Scheme Details:</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("SchemeManagerDlg", "Comments", None))

