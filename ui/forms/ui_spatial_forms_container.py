# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_spatial_forms_container.ui'
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

class Ui_SpatialFormsContainer(object):
    def setupUi(self, SpatialFormsContainer):
        SpatialFormsContainer.setObjectName(_fromUtf8("SpatialFormsContainer"))
        SpatialFormsContainer.resize(663, 673)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SpatialFormsContainer.sizePolicy().hasHeightForWidth())
        SpatialFormsContainer.setSizePolicy(sizePolicy)
        SpatialFormsContainer.setMinimumSize(QtCore.QSize(600, 400))
        self.verticalLayout = QtGui.QVBoxLayout(SpatialFormsContainer)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.str_notification = QtGui.QVBoxLayout()
        self.str_notification.setObjectName(_fromUtf8("str_notification"))
        self.horizontalLayout.addLayout(self.str_notification)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtGui.QSplitter(SpatialFormsContainer)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tree_view = QtGui.QTreeView(self.splitter)
        self.tree_view.setMaximumSize(QtCore.QSize(16777215, 350))
        self.tree_view.setAutoScrollMargin(16)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setObjectName(_fromUtf8("tree_view"))
        self.component_container = QtGui.QStackedWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.component_container.sizePolicy().hasHeightForWidth())
        self.component_container.setSizePolicy(sizePolicy)
        self.component_container.setFrameShape(QtGui.QFrame.StyledPanel)
        self.component_container.setMidLineWidth(0)
        self.component_container.setObjectName(_fromUtf8("component_container"))
        self.verticalLayout.addWidget(self.splitter)
        self.buttonBox = QtGui.QDialogButtonBox(SpatialFormsContainer)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SpatialFormsContainer)
        self.component_container.setCurrentIndex(-1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SpatialFormsContainer.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SpatialFormsContainer.reject)
        QtCore.QMetaObject.connectSlotsByName(SpatialFormsContainer)

    def retranslateUi(self, SpatialFormsContainer):
        SpatialFormsContainer.setWindowTitle(_translate("SpatialFormsContainer", "Spatial Entity Forms", None))
