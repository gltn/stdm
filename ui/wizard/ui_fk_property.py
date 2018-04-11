# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_fk_property.ui'
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

class Ui_FKProperty(object):
    def setupUi(self, FKProperty):
        FKProperty.setObjectName(_fromUtf8("FKProperty"))
        FKProperty.resize(353, 283)
        self.formLayout = QtGui.QFormLayout(FKProperty)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(FKProperty)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.cboPrimaryEntity = QtGui.QComboBox(FKProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboPrimaryEntity.sizePolicy().hasHeightForWidth())
        self.cboPrimaryEntity.setSizePolicy(sizePolicy)
        self.cboPrimaryEntity.setObjectName(_fromUtf8("cboPrimaryEntity"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.cboPrimaryEntity)
        self.label_2 = QtGui.QLabel(FKProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.cboPrimaryUKey = QtGui.QComboBox(FKProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboPrimaryUKey.sizePolicy().hasHeightForWidth())
        self.cboPrimaryUKey.setSizePolicy(sizePolicy)
        self.cboPrimaryUKey.setObjectName(_fromUtf8("cboPrimaryUKey"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.cboPrimaryUKey)
        self.label_3 = QtGui.QLabel(FKProperty)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.lvDisplayCol = QtGui.QListView(FKProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lvDisplayCol.sizePolicy().hasHeightForWidth())
        self.lvDisplayCol.setSizePolicy(sizePolicy)
        self.lvDisplayCol.setObjectName(_fromUtf8("lvDisplayCol"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.lvDisplayCol)
        self.buttonBox = QtGui.QDialogButtonBox(FKProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.show_in_parent_chk = QtGui.QCheckBox(FKProperty)
        self.show_in_parent_chk.setObjectName(_fromUtf8("show_in_parent_chk"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.show_in_parent_chk)
        self.show_in_child_chk = QtGui.QCheckBox(FKProperty)
        self.show_in_child_chk.setObjectName(_fromUtf8("show_in_child_chk"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.show_in_child_chk)

        self.retranslateUi(FKProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FKProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FKProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(FKProperty)

    def retranslateUi(self, FKProperty):
        FKProperty.setWindowTitle(_translate("FKProperty", "Foreign key editor", None))
        self.label.setText(_translate("FKProperty", "Primary entity", None))
        self.label_2.setText(_translate("FKProperty", "Primary unique column", None))
        self.label_3.setText(_translate("FKProperty", "Display columns", None))
        self.show_in_parent_chk.setText(_translate("FKProperty", "Show in parent form", None))
        self.show_in_child_chk.setText(_translate("FKProperty", "Show in child form", None))

