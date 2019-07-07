# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_report.ui'
#
# Created: Sat Jul  6 21:39:36 2019
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_Report_Dlg(object):
    def setupUi(self, Report_Dlg):
        Report_Dlg.setObjectName(_fromUtf8("Report_Dlg"))
        Report_Dlg.resize(482, 568)
        self.gridLayout = QtGui.QGridLayout(Report_Dlg)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame = QtGui.QFrame(Report_Dlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0, 20))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 201, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 2)
        self.frame_2 = QtGui.QFrame(Report_Dlg)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.radioButton = QtGui.QRadioButton(self.frame_2)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.gridLayout_2.addWidget(self.radioButton, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.frame_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 0, 2, 1, 1)
        self.comboBox = QtGui.QComboBox(self.frame_2)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout_2.addWidget(self.comboBox, 0, 3, 2, 1)
        self.radioButton_3 = QtGui.QRadioButton(self.frame_2)
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.gridLayout_2.addWidget(self.radioButton_3, 1, 1, 1, 1)
        self.radioButton_4 = QtGui.QRadioButton(self.frame_2)
        self.radioButton_4.setObjectName(_fromUtf8("radioButton_4"))
        self.gridLayout_2.addWidget(self.radioButton_4, 2, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.frame_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 3, 0, 1, 1)
        self.textEdit = QtGui.QTextEdit(self.frame_2)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout_2.addWidget(self.textEdit, 4, 0, 1, 4)
        self.gridLayout.addWidget(self.frame_2, 1, 0, 1, 2)
        self.pushButton_2 = QtGui.QPushButton(Report_Dlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout.addWidget(self.pushButton_2, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Report_Dlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)

        self.retranslateUi(Report_Dlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Report_Dlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Report_Dlg.reject)
        QtCore.QMetaObject.connectSlotsByName(Report_Dlg)

    def retranslateUi(self, Report_Dlg):
        Report_Dlg.setWindowTitle(_translate("Report_Dlg", "Dialog", None))
        self.label.setText(_translate("Report_Dlg", "Report FLTS", None))
        self.label_2.setText(_translate("Report_Dlg", "Generate report based on FLTS data", None))
        self.label_3.setText(_translate("Report_Dlg", "List:", None))
        self.radioButton.setText(_translate("Report_Dlg", "Holders", None))
        self.label_4.setText(_translate("Report_Dlg", "Sort with:", None))
        self.radioButton_3.setText(_translate("Report_Dlg", "Scheme", None))
        self.radioButton_4.setText(_translate("Report_Dlg", "Plots", None))
        self.label_5.setText(_translate("Report_Dlg", "Report details", None))
        self.pushButton_2.setText(_translate("Report_Dlg", "Export", None))

