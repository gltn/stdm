# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/nkoec/.qgis2/python/plugins/stdm/ui/flts/workflow_manager/ui_workflow_manager.ui'
#
# Created: Wed Dec 18 23:48:53 2019
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
        WorkflowManagerWidget.resize(837, 467)
        self.verticalLayout_2 = QtGui.QVBoxLayout(WorkflowManagerWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.verticalLayout.addLayout(self.vlNotification)
        self.toolbarFrame = QtGui.QFrame(WorkflowManagerWidget)
        self.toolbarFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.toolbarFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.toolbarFrame.setObjectName(_fromUtf8("toolbarFrame"))
        self.verticalLayout.addWidget(self.toolbarFrame)
        self.line = QtGui.QFrame(WorkflowManagerWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.tabWidget = QtGui.QTabWidget(WorkflowManagerWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.verticalLayout.addWidget(self.tabWidget)
        self.paginationFrame = QtGui.QFrame(WorkflowManagerWidget)
        self.paginationFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.paginationFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.paginationFrame.setObjectName(_fromUtf8("paginationFrame"))
        self.verticalLayout.addWidget(self.paginationFrame)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(WorkflowManagerWidget)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(WorkflowManagerWidget)

    def retranslateUi(self, WorkflowManagerWidget):
        WorkflowManagerWidget.setWindowTitle(_translate("WorkflowManagerWidget", "Workflow Manager", None))

