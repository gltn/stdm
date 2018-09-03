# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_spatial_forms.ui'
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

class Ui_SpatialForms(object):
    def setupUi(self, SpatialForms):
        SpatialForms.setObjectName(_fromUtf8("SpatialForms"))
        SpatialForms.resize(800, 600)
        self.centralwidget = QtGui.QWidget(SpatialForms)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.str_notification = QtGui.QVBoxLayout()
        self.str_notification.setObjectName(_fromUtf8("str_notification"))
        self.verticalLayout.addLayout(self.str_notification)
        self.tree_view = QtGui.QTreeView(self.centralwidget)
        self.tree_view.setMaximumSize(QtCore.QSize(16777215, 350))
        self.tree_view.setAutoScrollMargin(16)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setObjectName(_fromUtf8("tree_view"))
        self.verticalLayout.addWidget(self.tree_view)
        self.component_container = QtGui.QStackedWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.component_container.sizePolicy().hasHeightForWidth())
        self.component_container.setSizePolicy(sizePolicy)
        self.component_container.setFrameShape(QtGui.QFrame.StyledPanel)
        self.component_container.setMidLineWidth(0)
        self.component_container.setObjectName(_fromUtf8("component_container"))
        self.verticalLayout.addWidget(self.component_container)
        self.buttonBox = QtGui.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        SpatialForms.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(SpatialForms)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        SpatialForms.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(SpatialForms)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        SpatialForms.setStatusBar(self.statusbar)

        self.retranslateUi(SpatialForms)
        self.component_container.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(SpatialForms)

    def retranslateUi(self, SpatialForms):
        SpatialForms.setWindowTitle(_translate("SpatialForms", "MainWindow", None))

