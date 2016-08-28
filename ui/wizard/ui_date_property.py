# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_date_property.ui'
#
# Created: Wed Apr 27 08:56:35 2016
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
        DateProperty.resize(324, 233)
        self.formLayout = QtGui.QFormLayout(DateProperty)
        self.formLayout.setVerticalSpacing(20)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.groupBox_2 = QtGui.QGroupBox(DateProperty)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.rbMaxFixed = QtGui.QRadioButton(self.groupBox_2)
        self.rbMaxFixed.setObjectName(_fromUtf8("rbMaxFixed"))
        self.gridLayout_2.addWidget(self.rbMaxFixed, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 1, 1, 1)
        self.edtMaxDate = QtGui.QDateEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMaxDate.sizePolicy().hasHeightForWidth())
        self.edtMaxDate.setSizePolicy(sizePolicy)
        self.edtMaxDate.setCalendarPopup(True)
        self.edtMaxDate.setObjectName(_fromUtf8("edtMaxDate"))
        self.gridLayout_2.addWidget(self.edtMaxDate, 0, 2, 1, 1)
        self.rbMaxCurr = QtGui.QRadioButton(self.groupBox_2)
        self.rbMaxCurr.setObjectName(_fromUtf8("rbMaxCurr"))
        self.gridLayout_2.addWidget(self.rbMaxCurr, 1, 0, 1, 1)
        self.formLayout.setWidget(1, QtGui.QFormLayout.SpanningRole, self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(DateProperty)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.rbMinFixed = QtGui.QRadioButton(self.groupBox)
        self.rbMinFixed.setObjectName(_fromUtf8("rbMinFixed"))
        self.gridLayout.addWidget(self.rbMinFixed, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.edtMinDate = QtGui.QDateEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMinDate.sizePolicy().hasHeightForWidth())
        self.edtMinDate.setSizePolicy(sizePolicy)
        self.edtMinDate.setCalendarPopup(True)
        self.edtMinDate.setObjectName(_fromUtf8("edtMinDate"))
        self.gridLayout.addWidget(self.edtMinDate, 0, 2, 1, 1)
        self.rbMinCurr = QtGui.QRadioButton(self.groupBox)
        self.rbMinCurr.setObjectName(_fromUtf8("rbMinCurr"))
        self.gridLayout.addWidget(self.rbMinCurr, 1, 0, 1, 1)
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(DateProperty)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(DateProperty)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DateProperty.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DateProperty.reject)
        QtCore.QMetaObject.connectSlotsByName(DateProperty)

    def retranslateUi(self, DateProperty):
        DateProperty.setWindowTitle(_translate("DateProperty", "Date properties", None))
        self.groupBox_2.setTitle(_translate("DateProperty", "Maximum", None))
        self.rbMaxFixed.setText(_translate("DateProperty", "Fixed Date", None))
        self.label_2.setText(_translate("DateProperty", "Maximum date", None))
        self.rbMaxCurr.setText(_translate("DateProperty", "Current Date", None))
        self.groupBox.setTitle(_translate("DateProperty", "Minimum", None))
        self.rbMinFixed.setText(_translate("DateProperty", "Fixed Date", None))
        self.label.setText(_translate("DateProperty", "Minimum date", None))
        self.rbMinCurr.setText(_translate("DateProperty", "Current Date", None))

