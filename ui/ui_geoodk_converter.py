# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\SOLOMON\.qgis2\python\plugins\stdm\ui\ui_geoodk_converter.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(350, 579)
        self.gridLayout_4 = QtGui.QGridLayout(Dialog)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)
        self.txt_name = QtGui.QLineEdit(Dialog)
        self.txt_name.setObjectName(_fromUtf8("txt_name"))
        self.gridLayout_3.addWidget(self.txt_name, 1, 1, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 5, 0, 1, 1)
        self.vlnotification = QtGui.QVBoxLayout()
        self.vlnotification.setObjectName(_fromUtf8("vlnotification"))
        self.gridLayout_4.addLayout(self.vlnotification, 0, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.cboProf = QtGui.QComboBox(Dialog)
        self.cboProf.setObjectName(_fromUtf8("cboProf"))
        self.gridLayout_2.addWidget(self.cboProf, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 1, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.trentities = QtGui.QTreeView(self.groupBox_2)
        self.trentities.setObjectName(_fromUtf8("trentities"))
        self.gridLayout.addWidget(self.trentities, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.lstvwcolumns = QtGui.QListView(self.groupBox)
        self.lstvwcolumns.setObjectName(_fromUtf8("lstvwcolumns"))
        self.gridLayout_5.addWidget(self.lstvwcolumns, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.acceptDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "File Name", None))
        self.label_2.setText(_translate("Dialog", "Profile ", None))
        self.groupBox_2.setTitle(_translate("Dialog", "Entity List", None))
        self.label_3.setText(_translate("Dialog", "Select Entity", None))
        self.groupBox.setTitle(_translate("Dialog", "Select optional fields ", None))


