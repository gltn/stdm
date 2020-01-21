# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about_flts.ui'
#
# Created: Tue Jan 21 22:14:30 2020
#      by: PyQt4 UI code generator 4.10.2
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
        frmAbout.resize(718, 542)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmAbout.sizePolicy().hasHeightForWidth())
        frmAbout.setSizePolicy(sizePolicy)
        frmAbout.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayout = QtGui.QGridLayout(frmAbout)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
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
        self.txtAbout = QtGui.QTextEdit(frmAbout)
        self.txtAbout.setReadOnly(True)
        self.txtAbout.setObjectName(_fromUtf8("txtAbout"))
        self.gridLayout.addWidget(self.txtAbout, 0, 0, 1, 2)

        self.retranslateUi(frmAbout)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmAbout.reject)
        QtCore.QMetaObject.connectSlotsByName(frmAbout)

    def retranslateUi(self, frmAbout):
        frmAbout.setWindowTitle(_translate("frmAbout", "About FLTS", None))
        self.btnSTDMHome.setText(_translate("frmAbout", "MLR Website", None))
        self.btnContactUs.setText(_translate("frmAbout", "Contact", None))
        self.txtAbout.setDocumentTitle(_translate("frmAbout", "About FLTS", None))
        self.txtAbout.setHtml(_translate("frmAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><title>About FLTS</title><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:5pt; font-weight:200;\">    </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:36px; margin-right:36px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/plugins/stdm/images/icons/flts_2.png\" /></p>\n"
"<p style=\" margin-top:5px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">The goal of the Fexible Land Tenure System (FLTS) is to establish an interchangeable tenure registration system that is parallel and complementary to the initially existing systems. The<br />FLTS is designed to provide tenure security to informal settlement dwellers in Namibia in accordance to FLTA (Flexible Land Tenure Act). </span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\"> </span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\"><br /><br />This system</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\"> has the following tasks:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Uploading of land tenure information     </li>\n"
"<li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Quality checking / assessment</li>\n"
"<li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Revision of Scheme information</li>\n"
"<li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Uploading of spatial/plot data</li>\n"
"<li style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Certificate generation</li></ul>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt; font-weight:600;\">Objectives of FLTA</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\"><br /></span><span style=\" font-size:10pt;\">(a) to create alternative forms of landtitle that are simpler and cheaperto administer than existing forms of land title;</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">(b) to provide security of title for persons who live in informal settlements or who are provided<br />with low income housing;</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\"><br />(c) to empower the persons concerned economically by means of these rights </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:9pt;\"><br /><br />Copyright © 2020 UN Habitat and its implementing partners. All rights reserved.</span></p></body></html>", None))

from stdm import resources_rc
