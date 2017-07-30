# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_entity_attributes_editor.ui'
#
# Created: Sat Jul 29 10:33:35 2017
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EntityAttributesEditor(object):
    def setupUi(self, EntityAttributesEditor):
        EntityAttributesEditor.setObjectName(_fromUtf8("EntityAttributesEditor"))
        EntityAttributesEditor.resize(302, 359)
        self.gridLayout_2 = QtGui.QGridLayout(EntityAttributesEditor)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout_2.addLayout(self.vlNotification, 0, 0, 1, 2)
        self.label = QtGui.QLabel(EntityAttributesEditor)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.cbo_tenure_type = QtGui.QComboBox(EntityAttributesEditor)
        self.cbo_tenure_type.setObjectName(_fromUtf8("cbo_tenure_type"))
        self.gridLayout_2.addWidget(self.cbo_tenure_type, 1, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(EntityAttributesEditor)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnAddColumn = QtGui.QPushButton(self.groupBox)
        self.btnAddColumn.setMinimumSize(QtCore.QSize(30, 25))
        self.btnAddColumn.setMaximumSize(QtCore.QSize(30, 25))
        self.btnAddColumn.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAddColumn.setIcon(icon)
        self.btnAddColumn.setIconSize(QtCore.QSize(20, 20))
        self.btnAddColumn.setObjectName(_fromUtf8("btnAddColumn"))
        self.horizontalLayout_2.addWidget(self.btnAddColumn)
        self.btnEditColumn = QtGui.QPushButton(self.groupBox)
        self.btnEditColumn.setMinimumSize(QtCore.QSize(30, 25))
        self.btnEditColumn.setMaximumSize(QtCore.QSize(30, 25))
        self.btnEditColumn.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnEditColumn.setIcon(icon1)
        self.btnEditColumn.setIconSize(QtCore.QSize(20, 20))
        self.btnEditColumn.setObjectName(_fromUtf8("btnEditColumn"))
        self.horizontalLayout_2.addWidget(self.btnEditColumn)
        self.btnDeleteColumn = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDeleteColumn.sizePolicy().hasHeightForWidth())
        self.btnDeleteColumn.setSizePolicy(sizePolicy)
        self.btnDeleteColumn.setMinimumSize(QtCore.QSize(30, 25))
        self.btnDeleteColumn.setMaximumSize(QtCore.QSize(30, 25))
        self.btnDeleteColumn.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/delete.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnDeleteColumn.setIcon(icon2)
        self.btnDeleteColumn.setObjectName(_fromUtf8("btnDeleteColumn"))
        self.horizontalLayout_2.addWidget(self.btnDeleteColumn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.tb_view = AttributesTableView(self.groupBox)
        self.tb_view.setObjectName(_fromUtf8("tb_view"))
        self.gridLayout.addWidget(self.tb_view, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 2, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(EntityAttributesEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.retranslateUi(EntityAttributesEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EntityAttributesEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EntityAttributesEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(EntityAttributesEditor)

    def retranslateUi(self, EntityAttributesEditor):
        EntityAttributesEditor.setWindowTitle(QtGui.QApplication.translate("EntityAttributesEditor", "Custom Attributes Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EntityAttributesEditor", "Tenure type", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("EntityAttributesEditor", "Attributes:", None, QtGui.QApplication.UnicodeUTF8))

from stdm.ui.wizard.attributes_table_view import AttributesTableView
from stdm import resources_rc
