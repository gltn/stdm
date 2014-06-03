# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_food_crop_editor.ui'
#
# Created: Tue Apr 15 09:17:38 2014
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

class Ui_frmFoodCropEditor(object):
    def setupUi(self, frmFoodCropEditor):
        frmFoodCropEditor.setObjectName(_fromUtf8("frmFoodCropEditor"))
        frmFoodCropEditor.resize(284, 175)
        self.gridLayout = QtGui.QGridLayout(frmFoodCropEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(frmFoodCropEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.sbAcreage = QtGui.QDoubleSpinBox(frmFoodCropEditor)
        self.sbAcreage.setMinimumSize(QtCore.QSize(0, 30))
        self.sbAcreage.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.sbAcreage.setMaximum(100000.0)
        self.sbAcreage.setObjectName(_fromUtf8("sbAcreage"))
        self.gridLayout.addWidget(self.sbAcreage, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(frmFoodCropEditor)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label = QtGui.QLabel(frmFoodCropEditor)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(frmFoodCropEditor)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.cboCropCategory = QtGui.QComboBox(frmFoodCropEditor)
        self.cboCropCategory.setMinimumSize(QtCore.QSize(0, 30))
        self.cboCropCategory.setObjectName(_fromUtf8("cboCropCategory"))
        self.gridLayout.addWidget(self.cboCropCategory, 3, 1, 1, 1)
        self.txtCropName = QtGui.QLineEdit(frmFoodCropEditor)
        self.txtCropName.setMinimumSize(QtCore.QSize(0, 30))
        self.txtCropName.setMaxLength(100)
        self.txtCropName.setObjectName(_fromUtf8("txtCropName"))
        self.gridLayout.addWidget(self.txtCropName, 2, 1, 1, 1)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)

        self.retranslateUi(frmFoodCropEditor)
        QtCore.QMetaObject.connectSlotsByName(frmFoodCropEditor)

    def retranslateUi(self, frmFoodCropEditor):
        frmFoodCropEditor.setWindowTitle(_translate("frmFoodCropEditor", "Food Crop Editor", None))
        self.label_3.setText(_translate("frmFoodCropEditor", "Category", None))
        self.label.setText(_translate("frmFoodCropEditor", "Acreage", None))
        self.label_2.setText(_translate("frmFoodCropEditor", "Crop Name", None))

