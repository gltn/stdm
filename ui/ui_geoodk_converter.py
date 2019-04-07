# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geoodk_converter.ui'
#
# Created: Sun Apr 07 22:34:25 2019
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(404, 489)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.vlnotification = QtGui.QVBoxLayout()
        self.vlnotification.setObjectName(_fromUtf8("vlnotification"))
        self.verticalLayout.addLayout(self.vlnotification)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setHorizontalSpacing(200)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.chk_all = QtGui.QCheckBox(Dialog)
        self.chk_all.setObjectName(_fromUtf8("chk_all"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.chk_all)
        self.btnShowOutputFolder = QtGui.QPushButton(Dialog)
        self.btnShowOutputFolder.setObjectName(_fromUtf8("btnShowOutputFolder"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.btnShowOutputFolder)
        self.verticalLayout.addLayout(self.formLayout)
        self.trentities = QtGui.QTreeView(Dialog)
        self.trentities.setObjectName(_fromUtf8("trentities"))
        self.verticalLayout.addWidget(self.trentities)
        self.ck_social_tenure = QtGui.QCheckBox(Dialog)
        self.ck_social_tenure.setChecked(True)
        self.ck_social_tenure.setObjectName(_fromUtf8("ck_social_tenure"))
        self.verticalLayout.addWidget(self.ck_social_tenure)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("clicked(QAbstractButton*)")), Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "GeoODK Form Generator", None))
        self.label_3.setText(_translate("Dialog", "Select entities that will be exported to generated GeoODK form", None))
        self.chk_all.setText(_translate("Dialog", "Check all", None))
        self.btnShowOutputFolder.setText(_translate("Dialog", "Open output folder ...", None))
        self.ck_social_tenure.setText(_translate("Dialog", "Enable definition of social tenure relationship...", None))

