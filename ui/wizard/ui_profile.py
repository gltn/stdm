# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_profile.ui'
#
# Created: Sun Feb 21 15:23:48 2016
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

class Ui_Profile(object):
    def setupUi(self, Profile):
        Profile.setObjectName(_fromUtf8("Profile"))
        Profile.resize(358, 140)
        self.edtDesc = QtGui.QLineEdit(Profile)
        self.edtDesc.setGeometry(QtCore.QRect(90, 52, 261, 20))
        self.edtDesc.setObjectName(_fromUtf8("edtDesc"))
        self.label_2 = QtGui.QLabel(Profile)
        self.label_2.setGeometry(QtCore.QRect(25, 52, 53, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label = QtGui.QLabel(Profile)
        self.label.setGeometry(QtCore.QRect(25, 20, 59, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.buttonBox = QtGui.QDialogButtonBox(Profile)
        self.buttonBox.setGeometry(QtCore.QRect(190, 90, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.edtProfile = QtGui.QLineEdit(Profile)
        self.edtProfile.setGeometry(QtCore.QRect(90, 20, 261, 20))
        self.edtProfile.setObjectName(_fromUtf8("edtProfile"))

        self.retranslateUi(Profile)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Profile.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Profile.reject)
        QtCore.QMetaObject.connectSlotsByName(Profile)
        Profile.setTabOrder(self.edtProfile, self.edtDesc)
        Profile.setTabOrder(self.edtDesc, self.buttonBox)

    def retranslateUi(self, Profile):
        Profile.setWindowTitle(_translate("Profile", "Profile Editor", None))
        self.edtDesc.setPlaceholderText(_translate("Profile", "Profile description", None))
        self.label_2.setText(_translate("Profile", "Description", None))
        self.label.setText(_translate("Profile", "Profile name", None))
        self.edtProfile.setPlaceholderText(_translate("Profile", "Profile name", None))

