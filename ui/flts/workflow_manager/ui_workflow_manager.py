# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/nkoec/.qgis2/python/plugins/stdm/ui/flts/workflow_manager/ui_workflow_manager.ui'
#
# Created: Thu Aug 22 23:13:49 2019
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

class Ui_WorkflowManagerWidget(object):
    def setupUi(self, WorkflowManagerWidget):
        WorkflowManagerWidget.setObjectName(_fromUtf8("WorkflowManagerWidget"))
        WorkflowManagerWidget.resize(1043, 745)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(WorkflowManagerWidget)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.verticalLayout.addLayout(self.vlNotification)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.approveButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.approveButton.setEnabled(False)
        self.approveButton.setObjectName(_fromUtf8("approveButton"))
        self.horizontalLayout.addWidget(self.approveButton)
        self.disapproveButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.disapproveButton.setEnabled(False)
        self.disapproveButton.setObjectName(_fromUtf8("disapproveButton"))
        self.horizontalLayout.addWidget(self.disapproveButton)
        self.holdersButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.holdersButton.setEnabled(False)
        self.holdersButton.setObjectName(_fromUtf8("holdersButton"))
        self.horizontalLayout.addWidget(self.holdersButton)
        self.documentsButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.documentsButton.setEnabled(False)
        self.documentsButton.setObjectName(_fromUtf8("documentsButton"))
        self.horizontalLayout.addWidget(self.documentsButton)
        spacerItem = QtGui.QSpacerItem(178, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.searchEdit = QtGui.QLineEdit(WorkflowManagerWidget)
        self.searchEdit.setEnabled(False)
        self.searchEdit.setObjectName(_fromUtf8("searchEdit"))
        self.horizontalLayout.addWidget(self.searchEdit)
        self.filterComboBox = QtGui.QComboBox(WorkflowManagerWidget)
        self.filterComboBox.setEnabled(False)
        self.filterComboBox.setObjectName(_fromUtf8("filterComboBox"))
        self.filterComboBox.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.filterComboBox)
        self.searchButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.searchButton.setEnabled(False)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.horizontalLayout.addWidget(self.searchButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtGui.QFrame(WorkflowManagerWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.tabWidget = QtGui.QTabWidget(WorkflowManagerWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.firstButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.firstButton.setEnabled(False)
        self.firstButton.setObjectName(_fromUtf8("firstButton"))
        self.horizontalLayout_2.addWidget(self.firstButton)
        self.previousButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.previousButton.setEnabled(False)
        self.previousButton.setObjectName(_fromUtf8("previousButton"))
        self.horizontalLayout_2.addWidget(self.previousButton)
        self.paginationEdit = QtGui.QLineEdit(WorkflowManagerWidget)
        self.paginationEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.paginationEdit.setObjectName(_fromUtf8("paginationEdit"))
        self.horizontalLayout_2.addWidget(self.paginationEdit)
        self.nextButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.nextButton.setEnabled(False)
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.horizontalLayout_2.addWidget(self.nextButton)
        self.lastButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.lastButton.setEnabled(False)
        self.lastButton.setObjectName(_fromUtf8("lastButton"))
        self.horizontalLayout_2.addWidget(self.lastButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(WorkflowManagerWidget)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(WorkflowManagerWidget)

    def retranslateUi(self, WorkflowManagerWidget):
        WorkflowManagerWidget.setWindowTitle(_translate("WorkflowManagerWidget", "Workflow Manager", None))
        self.approveButton.setText(_translate("WorkflowManagerWidget", "Approve", None))
        self.disapproveButton.setText(_translate("WorkflowManagerWidget", "Disapprove", None))
        self.holdersButton.setText(_translate("WorkflowManagerWidget", "Holders", None))
        self.documentsButton.setText(_translate("WorkflowManagerWidget", "Documents", None))
        self.searchEdit.setPlaceholderText(_translate("WorkflowManagerWidget", "Type to search...", None))
        self.filterComboBox.setItemText(0, _translate("WorkflowManagerWidget", "Apply Filter", None))
        self.searchButton.setText(_translate("WorkflowManagerWidget", "Search", None))
        self.firstButton.setText(_translate("WorkflowManagerWidget", "First", None))
        self.previousButton.setText(_translate("WorkflowManagerWidget", "Previous", None))
        self.paginationEdit.setText(_translate("WorkflowManagerWidget", "No Records Found", None))
        self.nextButton.setText(_translate("WorkflowManagerWidget", "Next", None))
        self.lastButton.setText(_translate("WorkflowManagerWidget", "Last", None))

