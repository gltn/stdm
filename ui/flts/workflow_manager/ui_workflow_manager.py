# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/nkoec/.qgis2/python/plugins/stdm/ui/flts/workflow_manager/ui_workflow_manager.ui'
#
# Created: Tue Aug 20 07:54:06 2019
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
        self.horizontalLayout = QtGui.QHBoxLayout(WorkflowManagerWidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.verticalLayout.addLayout(self.vlNotification)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.approveButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.approveButton.setObjectName(_fromUtf8("approveButton"))
        self.horizontalLayout_3.addWidget(self.approveButton)
        self.disapproveButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.disapproveButton.setObjectName(_fromUtf8("disapproveButton"))
        self.horizontalLayout_3.addWidget(self.disapproveButton)
        self.saveButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.horizontalLayout_3.addWidget(self.saveButton)
        spacerItem = QtGui.QSpacerItem(98, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.searchEdit = QtGui.QLineEdit(WorkflowManagerWidget)
        self.searchEdit.setObjectName(_fromUtf8("searchEdit"))
        self.horizontalLayout_3.addWidget(self.searchEdit)
        self.filterComboBox = QtGui.QComboBox(WorkflowManagerWidget)
        self.filterComboBox.setObjectName(_fromUtf8("filterComboBox"))
        self.filterComboBox.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.filterComboBox)
        self.searchButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.horizontalLayout_3.addWidget(self.searchButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.line = QtGui.QFrame(WorkflowManagerWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.tabWidget = QtGui.QTabWidget(WorkflowManagerWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.verticalLayout.addWidget(self.tabWidget)
        self.paginationLayout = QtGui.QHBoxLayout()
        self.paginationLayout.setObjectName(_fromUtf8("paginationLayout"))
        self.firstButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.firstButton.setObjectName(_fromUtf8("firstButton"))
        self.paginationLayout.addWidget(self.firstButton)
        self.previousButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.previousButton.setObjectName(_fromUtf8("previousButton"))
        self.paginationLayout.addWidget(self.previousButton)
        self.paginationEdit = QtGui.QLineEdit(WorkflowManagerWidget)
        self.paginationEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.paginationEdit.setObjectName(_fromUtf8("paginationEdit"))
        self.paginationLayout.addWidget(self.paginationEdit)
        self.nextButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.paginationLayout.addWidget(self.nextButton)
        self.lastButton = QtGui.QPushButton(WorkflowManagerWidget)
        self.lastButton.setObjectName(_fromUtf8("lastButton"))
        self.paginationLayout.addWidget(self.lastButton)
        self.verticalLayout.addLayout(self.paginationLayout)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(WorkflowManagerWidget)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(WorkflowManagerWidget)

    def retranslateUi(self, WorkflowManagerWidget):
        WorkflowManagerWidget.setWindowTitle(_translate("WorkflowManagerWidget", "Workflow Manager", None))
        self.approveButton.setText(_translate("WorkflowManagerWidget", "Approve", None))
        self.disapproveButton.setText(_translate("WorkflowManagerWidget", "Disapprove", None))
        self.saveButton.setText(_translate("WorkflowManagerWidget", "Save", None))
        self.searchEdit.setPlaceholderText(_translate("WorkflowManagerWidget", "Type to search...", None))
        self.filterComboBox.setItemText(0, _translate("WorkflowManagerWidget", "Apply Filter", None))
        self.searchButton.setText(_translate("WorkflowManagerWidget", "Search", None))
        self.firstButton.setText(_translate("WorkflowManagerWidget", "First", None))
        self.previousButton.setText(_translate("WorkflowManagerWidget", "Previous", None))
        self.paginationEdit.setText(_translate("WorkflowManagerWidget", "No Records Found", None))
        self.nextButton.setText(_translate("WorkflowManagerWidget", "Next", None))
        self.lastButton.setText(_translate("WorkflowManagerWidget", "Last", None))

