# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dtime_property.ui'
#
# Created: Sun Apr 24 14:30:19 2016
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

class Ui_DTimeProperty(object):
    def setupUi(self, DTimeProperty):
        DTimeProperty.setObjectName(_fromUtf8("DTimeProperty"))
        DTimeProperty.resize(246, 106)
        self.formLayout = QtGui.QFormLayout(DTimeProperty)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DTimeProperty)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtMinDTime = QtGui.QDateTimeEdit(DTimeProperty)
        self.edtMinDTime.setCalendarPopup(True)
        self.edtMinDTime.setObjectName(_fromUtf8("edtMinDTime"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtMinDTime)
        self.label_2 = QtGui.QLabel(DTimeProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtMaxDTime = QtGui.QDateTimeEdit(DTimeProperty)
        self.edtMaxDTime.setCalendarPopup(True)
        self.edtMaxDTime.setObjectName(_fromUtf8("edtMaxDTime"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtMaxDTime)
        self.buttonBox = QtGui.QDialogButtonBox(DTimeProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(DTimeProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DTimeProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DTimeProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(DTimeProperty)

    def retranslateUi(self, DTimeProperty):
        DTimeProperty.setWindowTitle(_translate("DTimeProperty", "Datetime properties", None))
        self.label.setText(_translate("DTimeProperty", "Minimum date", None))
        self.label_2.setText(_translate("DTimeProperty", "Maximum date", None))

