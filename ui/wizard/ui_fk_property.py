# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_fk_property.ui'
#
# Created: Mon Feb 22 11:52:09 2016
#      by: PyQt4 UI code generator 4.11.3
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
        FKProperty.resize(320, 240)
        self.buttonBox = QtGui.QDialogButtonBox(FKProperty)
        self.buttonBox.setGeometry(QtCore.QRect(150, 210, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.cboPrimaryUKey = QtGui.QComboBox(FKProperty)
        self.cboPrimaryUKey.setGeometry(QtCore.QRect(120, 34, 191, 20))
        self.cboPrimaryUKey.setObjectName(_fromUtf8("cboPrimaryUKey"))
        self.label_2 = QtGui.QLabel(FKProperty)
        self.label_2.setGeometry(QtCore.QRect(7, 34, 107, 16))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(FKProperty)
        self.label_3.setGeometry(QtCore.QRect(7, 60, 75, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cboPrimaryEntity = QtGui.QComboBox(FKProperty)
        self.cboPrimaryEntity.setGeometry(QtCore.QRect(120, 8, 191, 20))
        self.cboPrimaryEntity.setObjectName(_fromUtf8("cboPrimaryEntity"))
        self.label = QtGui.QLabel(FKProperty)
        self.label.setGeometry(QtCore.QRect(7, 8, 67, 16))
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.lvDisplayCol = QtGui.QListView(FKProperty)
        self.lvDisplayCol.setGeometry(QtCore.QRect(120, 60, 191, 142))
        self.lvDisplayCol.setObjectName(_fromUtf8("lvDisplayCol"))

        self.retranslateUi(FKProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FKProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FKProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(FKProperty)

    def retranslateUi(self, FKProperty):
        FKProperty.setWindowTitle(_translate("FKProperty", "Foreign key editor", None))
        self.label_2.setText(_translate("FKProperty", "Primary unique column", None))
        self.label_3.setText(_translate("FKProperty", "Display columns", None))
        self.label.setText(_translate("FKProperty", "Primary entity", None))

