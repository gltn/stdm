# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_profile.ui'
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

class Ui_Profile(object):
    def setupUi(self, Profile):
        Profile.setObjectName(_fromUtf8("Profile"))
        Profile.resize(329, 153)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Profile)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.notif_bar = QtGui.QVBoxLayout()
        self.notif_bar.setObjectName(_fromUtf8("notif_bar"))
        self.verticalLayout_2.addLayout(self.notif_bar)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Profile)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtProfile = QtGui.QLineEdit(Profile)
        self.edtProfile.setObjectName(_fromUtf8("edtProfile"))
        self.gridLayout.addWidget(self.edtProfile, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Profile)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.edtDesc = QtGui.QLineEdit(Profile)
        self.edtDesc.setObjectName(_fromUtf8("edtDesc"))
        self.gridLayout.addWidget(self.edtDesc, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Profile)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Profile)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Profile.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Profile.reject)
        QtCore.QMetaObject.connectSlotsByName(Profile)
        Profile.setTabOrder(self.edtProfile, self.buttonBox)

    def retranslateUi(self, Profile):
        Profile.setWindowTitle(_translate("Profile", "Profile Editor", None))
        self.label.setText(_translate("Profile", "Profile name", None))
        self.edtProfile.setPlaceholderText(_translate("Profile", "Profile name", None))
        self.label_2.setText(_translate("Profile", "Description", None))
        self.edtDesc.setPlaceholderText(_translate("Profile", "Profile description", None))

