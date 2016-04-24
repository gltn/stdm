# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_date_property.ui'
#
# Created: Sun Apr 24 14:29:52 2016
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

class Ui_DateProperty(object):
    def setupUi(self, DateProperty):
        DateProperty.setObjectName(_fromUtf8("DateProperty"))
        DateProperty.resize(245, 104)
        self.formLayout = QtGui.QFormLayout(DateProperty)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DateProperty)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edtMinDate = QtGui.QDateEdit(DateProperty)
        self.edtMinDate.setCalendarPopup(True)
        self.edtMinDate.setObjectName(_fromUtf8("edtMinDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtMinDate)
        self.label_2 = QtGui.QLabel(DateProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edtMaxDate = QtGui.QDateEdit(DateProperty)
        self.edtMaxDate.setCalendarPopup(True)
        self.edtMaxDate.setObjectName(_fromUtf8("edtMaxDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtMaxDate)
        self.buttonBox = QtGui.QDialogButtonBox(DateProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(DateProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DateProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DateProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(DateProperty)

    def retranslateUi(self, DateProperty):
        DateProperty.setWindowTitle(_translate("DateProperty", "Date properties", None))
        self.label.setText(_translate("DateProperty", "Minimum date", None))
        self.label_2.setText(_translate("DateProperty", "Maximum date", None))

