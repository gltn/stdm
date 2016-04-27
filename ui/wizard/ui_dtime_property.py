# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dtime_property.ui'
#
# Created: Wed Apr 27 11:31:21 2016
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
        DTimeProperty.resize(341, 233)
        self.formLayout = QtGui.QFormLayout(DTimeProperty)
        self.formLayout.setVerticalSpacing(20)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.groupBox = QtGui.QGroupBox(DTimeProperty)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.rbMinFixed = QtGui.QRadioButton(self.groupBox)
        self.rbMinFixed.setChecked(True)
        self.rbMinFixed.setObjectName(_fromUtf8("rbMinFixed"))
        self.gridLayout.addWidget(self.rbMinFixed, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(200, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.edtMinDTime = QtGui.QDateTimeEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMinDTime.sizePolicy().hasHeightForWidth())
        self.edtMinDTime.setSizePolicy(sizePolicy)
        self.edtMinDTime.setCalendarPopup(True)
        self.edtMinDTime.setObjectName(_fromUtf8("edtMinDTime"))
        self.gridLayout.addWidget(self.edtMinDTime, 0, 2, 1, 1)
        self.rbMinCurr = QtGui.QRadioButton(self.groupBox)
        self.rbMinCurr.setObjectName(_fromUtf8("rbMinCurr"))
        self.gridLayout.addWidget(self.rbMinCurr, 1, 0, 1, 1)
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(DTimeProperty)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.rbMaxFixed = QtGui.QRadioButton(self.groupBox_2)
        self.rbMaxFixed.setChecked(True)
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
        self.edtMaxDTime = QtGui.QDateTimeEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMaxDTime.sizePolicy().hasHeightForWidth())
        self.edtMaxDTime.setSizePolicy(sizePolicy)
        self.edtMaxDTime.setCalendarPopup(True)
        self.edtMaxDTime.setObjectName(_fromUtf8("edtMaxDTime"))
        self.gridLayout_2.addWidget(self.edtMaxDTime, 0, 2, 1, 1)
        self.rbMaxCurr = QtGui.QRadioButton(self.groupBox_2)
        self.rbMaxCurr.setObjectName(_fromUtf8("rbMaxCurr"))
        self.gridLayout_2.addWidget(self.rbMaxCurr, 1, 0, 1, 1)
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.groupBox_2)
        self.buttonBox = QtGui.QDialogButtonBox(DTimeProperty)
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
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
        self.groupBox.setTitle(_translate("DTimeProperty", "Minimum", None))
        self.rbMinFixed.setText(_translate("DTimeProperty", "Fixed Date", None))
        self.label.setText(_translate("DTimeProperty", "Minimum date", None))
        self.rbMinCurr.setText(_translate("DTimeProperty", "Current Date", None))
        self.groupBox_2.setTitle(_translate("DTimeProperty", "Maximum", None))
        self.rbMaxFixed.setText(_translate("DTimeProperty", "Fixed Date", None))
        self.label_2.setText(_translate("DTimeProperty", "Maximum date", None))
        self.rbMaxCurr.setText(_translate("DTimeProperty", "Current Date", None))

