# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_double_property.ui'
#
# Created: Wed Mar 01 12:08:28 2017
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DoubleProperty(object):
    def setupUi(self, DoubleProperty):
        DoubleProperty.setObjectName(_fromUtf8("DoubleProperty"))
        DoubleProperty.resize(258, 151)
        self.gridLayout = QtGui.QGridLayout(DoubleProperty)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(DoubleProperty)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.sbPrecision = QtGui.QSpinBox(DoubleProperty)
        self.sbPrecision.setMinimum(1)
        self.sbPrecision.setMaximum(50)
        self.sbPrecision.setProperty("value", 1)
        self.sbPrecision.setObjectName(_fromUtf8("sbPrecision"))
        self.gridLayout.addWidget(self.sbPrecision, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(DoubleProperty)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.sbScale = QtGui.QSpinBox(DoubleProperty)
        self.sbScale.setMaximum(20)
        self.sbScale.setObjectName(_fromUtf8("sbScale"))
        self.gridLayout.addWidget(self.sbScale, 1, 1, 1, 1)
        self.label = QtGui.QLabel(DoubleProperty)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.edtMinVal = QtGui.QLineEdit(DoubleProperty)
        self.edtMinVal.setObjectName(_fromUtf8("edtMinVal"))
        self.gridLayout.addWidget(self.edtMinVal, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(DoubleProperty)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.edtMaxVal = QtGui.QLineEdit(DoubleProperty)
        self.edtMaxVal.setObjectName(_fromUtf8("edtMaxVal"))
        self.gridLayout.addWidget(self.edtMaxVal, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(DoubleProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(DoubleProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DoubleProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DoubleProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(DoubleProperty)

    def retranslateUi(self, DoubleProperty):
        DoubleProperty.setWindowTitle(QtGui.QApplication.translate("DoubleProperty", "Decimal Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("DoubleProperty", "Precision", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("DoubleProperty", "Scale", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DoubleProperty", "Minimum value", None, QtGui.QApplication.UnicodeUTF8))
        self.edtMinVal.setPlaceholderText(QtGui.QApplication.translate("DoubleProperty", "Enter minimum value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("DoubleProperty", "Maximum value", None, QtGui.QApplication.UnicodeUTF8))
        self.edtMaxVal.setPlaceholderText(QtGui.QApplication.translate("DoubleProperty", "Enter maximum value", None, QtGui.QApplication.UnicodeUTF8))

