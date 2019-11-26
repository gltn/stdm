# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about_stdm.ui'
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

class Ui_frmAbout(object):
    def setupUi(self, frmAbout):
        frmAbout.setObjectName(_fromUtf8("frmAbout"))
        frmAbout.resize(718, 541)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmAbout.sizePolicy().hasHeightForWidth())
        frmAbout.setSizePolicy(sizePolicy)
        frmAbout.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayout = QtGui.QGridLayout(frmAbout)
        self.gridLayout.setMargin(9)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtAbout = QtGui.QTextEdit(frmAbout)
        self.txtAbout.setReadOnly(True)
        self.txtAbout.setObjectName(_fromUtf8("txtAbout"))
        self.gridLayout.addWidget(self.txtAbout, 0, 0, 1, 2)
        self.btnSTDMHome = QtGui.QPushButton(frmAbout)
        self.btnSTDMHome.setMinimumSize(QtCore.QSize(0, 30))
        self.btnSTDMHome.setObjectName(_fromUtf8("btnSTDMHome"))
        self.gridLayout.addWidget(self.btnSTDMHome, 1, 0, 1, 1)
        self.btnContactUs = QtGui.QPushButton(frmAbout)
        self.btnContactUs.setMinimumSize(QtCore.QSize(0, 30))
        self.btnContactUs.setObjectName(_fromUtf8("btnContactUs"))
        self.gridLayout.addWidget(self.btnContactUs, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmAbout)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi(frmAbout)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmAbout.reject)
        QtCore.QMetaObject.connectSlotsByName(frmAbout)

    def retranslateUi(self, frmAbout):
        frmAbout.setWindowTitle(_translate("frmAbout", "About DR Congo SIF", None))
        self.txtAbout.setHtml(_translate("frmAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><title>About DR Congo SIF</title><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.5pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:36px; margin-right:36px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:5pt; font-weight:200;\">    </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:36px; margin-right:36px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/plugins/stdm/images/icons/stdm_2.png\" /><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:14pt; font-weight:600;\">    </span></p>\n"
"<p style=\" margin-top:5px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\">DR Congo SIF is based on the Social Tenure Domain Model (STDM) is a pro poor, gender responsive and participatory land rights recordation developed by the Global Land Tool Network (GLTN) for the promotion of secure land and property rights for all. It broadens the scope of land administration by incorporating all person/s to land relationships beyond formal/legal land rights, cognisant of the continuum of land rights. <br /><br />STDM has four inter-related components:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A new way of thinking about land records    </li>\n"
"<li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A free and open-source software package to record information about land    </li>\n"
"<li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">An approach of collecting data about land    </li>\n"
"<li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A way of using and disseminating information about land</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt; font-weight:600;\">Core Values</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\"><br />STDM\'s core values and principles are pro-poor, good governance, equity, subsidiarity, sustainability, affordability, systematic large scale, and gender responsiveness.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\"><br /><br />Copyright © 2018 UN Habitat and its implementing partners. All rights reserved.</span></p></body></html>", None))
        self.btnSTDMHome.setText(_translate("frmAbout", "STDM Home Page", None))
        self.btnContactUs.setText(_translate("frmAbout", "Contact Us", None))

from stdm import resources_rc
