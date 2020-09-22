# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_license_agreement.ui'
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

class Ui_LicenseAgreement(object):
    def setupUi(self, LicenseAgreement):
        LicenseAgreement.setObjectName(_fromUtf8("LicenseAgreement"))
        LicenseAgreement.resize(714, 557)
        self.verticalLayout = QtGui.QVBoxLayout(LicenseAgreement)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.notifBar = QtGui.QVBoxLayout()
        self.notifBar.setObjectName(_fromUtf8("notifBar"))
        self.verticalLayout.addLayout(self.notifBar)
        self.widget = QtGui.QWidget(LicenseAgreement)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_3.addWidget(self.label)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_3.addWidget(self.label_2)
        self.verticalLayout.addWidget(self.widget)
        self.groupBox = QtGui.QGroupBox(LicenseAgreement)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.scrollArea = QtGui.QScrollArea(self.groupBox)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.termsCondCont = QtGui.QWidget()
        self.termsCondCont.setGeometry(QtCore.QRect(0, 0, 690, 369))
        self.termsCondCont.setObjectName(_fromUtf8("termsCondCont"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.termsCondCont)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.termsCond = QtGui.QVBoxLayout()
        self.termsCond.setSpacing(0)
        self.termsCond.setObjectName(_fromUtf8("termsCond"))
        self.termsCondArea = QtGui.QTextEdit(self.termsCondCont)
        self.termsCondArea.setReadOnly(True)
        self.termsCondArea.setObjectName(_fromUtf8("termsCondArea"))
        self.termsCond.addWidget(self.termsCondArea)
        self.verticalLayout_5.addLayout(self.termsCond)
        self.scrollArea.setWidget(self.termsCondCont)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.groupBox)
        self.checkBoxAgree = QtGui.QCheckBox(LicenseAgreement)
        self.checkBoxAgree.setObjectName(_fromUtf8("checkBoxAgree"))
        self.verticalLayout.addWidget(self.checkBoxAgree)
        self.buttonBox = QtGui.QDialogButtonBox(LicenseAgreement)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnAccept = QtGui.QPushButton(LicenseAgreement)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAccept.sizePolicy().hasHeightForWidth())
        self.btnAccept.setSizePolicy(sizePolicy)
        self.btnAccept.setObjectName(_fromUtf8("btnAccept"))
        self.horizontalLayout.addWidget(self.btnAccept)
        self.btnDecline = QtGui.QPushButton(LicenseAgreement)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDecline.sizePolicy().hasHeightForWidth())
        self.btnDecline.setSizePolicy(sizePolicy)
        self.btnDecline.setObjectName(_fromUtf8("btnDecline"))
        self.horizontalLayout.addWidget(self.btnDecline)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(LicenseAgreement)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LicenseAgreement.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LicenseAgreement.reject)
        QtCore.QMetaObject.connectSlotsByName(LicenseAgreement)

    def retranslateUi(self, LicenseAgreement):
        LicenseAgreement.setWindowTitle(_translate("LicenseAgreement", "License Agreement", None))
        self.label.setText(_translate("LicenseAgreement", "End User License Agreement", None))
        self.label_2.setText(_translate("LicenseAgreement", "Please read carefully before you proceed. You must accept the terms and condititions to access the plugin. ", None))
        self.groupBox.setTitle(_translate("LicenseAgreement", "Terms and Conditions", None))
        self.checkBoxAgree.setText(_translate("LicenseAgreement", "I have read and agree to the terms and conditions ", None))
        self.btnAccept.setText(_translate("LicenseAgreement", "Accept", None))
        self.btnDecline.setText(_translate("LicenseAgreement", "Decline", None))

