# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_profile.ui'
#
# Created: Sun Apr 27 17:15:47 2014
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

class Ui_Profile(object):
    def setupUi(self, Profile):
        Profile.setObjectName(_fromUtf8("Profile"))
        Profile.resize(404, 196)
        self.gridLayout = QtGui.QGridLayout(Profile)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(Profile)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.txtProfile = QtGui.QLineEdit(self.groupBox)
        self.txtProfile.setObjectName(_fromUtf8("txtProfile"))
        self.gridLayout_2.addWidget(self.txtProfile, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtDesc = QtGui.QLineEdit(self.groupBox)
        self.txtDesc.setObjectName(_fromUtf8("txtDesc"))
        self.gridLayout_2.addWidget(self.txtDesc, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Profile)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Profile)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Profile.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Profile.reject)
        QtCore.QMetaObject.connectSlotsByName(Profile)

    def retranslateUi(self, Profile):
        Profile.setWindowTitle(_translate("Profile", "Profile Editor", None))
        self.groupBox.setTitle(_translate("Profile", "Manage Profile", None))
        self.label.setText(_translate("Profile", "Profile Name", None))
        self.txtProfile.setPlaceholderText(_translate("Profile", "Profile name", None))
        self.label_2.setText(_translate("Profile", "Description", None))
        self.txtDesc.setPlaceholderText(_translate("Profile", "Profile description", None))

