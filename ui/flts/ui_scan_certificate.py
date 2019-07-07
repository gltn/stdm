# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_scan_certificate.ui'
#
# Created: Sat Jul  6 21:39:09 2019
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

class Ui_ScanCert_Dlg(object):
    def setupUi(self, ScanCert_Dlg):
        ScanCert_Dlg.setObjectName(_fromUtf8("ScanCert_Dlg"))
        ScanCert_Dlg.resize(463, 288)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ScanCert_Dlg.sizePolicy().hasHeightForWidth())
        ScanCert_Dlg.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(ScanCert_Dlg)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(ScanCert_Dlg)
        self.label_2.setMinimumSize(QtCore.QSize(0, 50))
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.frame_2 = QtGui.QFrame(ScanCert_Dlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 100))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.label = QtGui.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(15, 30, 81, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.selectScanner_Cbx = QtGui.QComboBox(self.frame_2)
        self.selectScanner_Cbx.setGeometry(QtCore.QRect(110, 30, 191, 22))
        self.selectScanner_Cbx.setObjectName(_fromUtf8("selectScanner_Cbx"))
        self.gridLayout.addWidget(self.frame_2, 1, 0, 1, 1)
        self.ScanCert_Label = QtGui.QLabel(ScanCert_Dlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ScanCert_Label.sizePolicy().hasHeightForWidth())
        self.ScanCert_Label.setSizePolicy(sizePolicy)
        self.ScanCert_Label.setObjectName(_fromUtf8("ScanCert_Label"))
        self.gridLayout.addWidget(self.ScanCert_Label, 2, 0, 1, 1)
        self.frame = QtGui.QFrame(ScanCert_Dlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.pushButton = QtGui.QPushButton(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_2.addWidget(self.pushButton, 2, 0, 1, 1)
        self.cancelBtn = QtGui.QPushButton(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelBtn.sizePolicy().hasHeightForWidth())
        self.cancelBtn.setSizePolicy(sizePolicy)
        self.cancelBtn.setObjectName(_fromUtf8("cancelBtn"))
        self.gridLayout_2.addWidget(self.cancelBtn, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.frame, 3, 0, 1, 1)

        self.retranslateUi(ScanCert_Dlg)
        QtCore.QObject.connect(self.cancelBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), ScanCert_Dlg.accept)
        QtCore.QMetaObject.connectSlotsByName(ScanCert_Dlg)

    def retranslateUi(self, ScanCert_Dlg):
        ScanCert_Dlg.setWindowTitle(_translate("ScanCert_Dlg", "Scan Certificate", None))
        self.label_2.setText(_translate("ScanCert_Dlg", "THis window shows available options for scanning of certificate", None))
        self.label.setText(_translate("ScanCert_Dlg", "Select Scanner:", None))
        self.selectScanner_Cbx.setToolTip(_translate("ScanCert_Dlg", "<html><head/><body><p>Select a scanner</p></body></html>", None))
        self.ScanCert_Label.setText(_translate("ScanCert_Dlg", "Click scan to scan certificate and cancel to exit window", None))
        self.pushButton.setText(_translate("ScanCert_Dlg", "Scan", None))
        self.cancelBtn.setText(_translate("ScanCert_Dlg", "cancel", None))

