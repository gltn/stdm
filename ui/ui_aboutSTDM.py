# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_aboutSTDM.ui'
#
# Created: Tue Jun  3 09:26:17 2014
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

class Ui_frmAbout(object):
    def setupUi(self, frmAbout):
        frmAbout.setObjectName(_fromUtf8("frmAbout"))
        frmAbout.resize(579, 565)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(frmAbout.sizePolicy().hasHeightForWidth())
        frmAbout.setSizePolicy(sizePolicy)
        frmAbout.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.layoutWidget = QtGui.QWidget(frmAbout)
        self.layoutWidget.setGeometry(QtCore.QRect(9, 9, 561, 531))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtAbout = QtGui.QTextEdit(self.layoutWidget)
        self.txtAbout.setReadOnly(True)
        self.txtAbout.setObjectName(_fromUtf8("txtAbout"))
        self.gridLayout.addWidget(self.txtAbout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(frmAbout)
        QtCore.QMetaObject.connectSlotsByName(frmAbout)

    def retranslateUi(self, frmAbout):
        frmAbout.setWindowTitle(_translate("frmAbout", "About STDM", None))
        self.txtAbout.setHtml(_translate("frmAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:6px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt; background-color:#ffffff;\"><br /></p>\n"
"<p style=\" margin-top:6px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000; background-color:#ffffff;\">The</span><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\"> </span><a href=\"http://www.stdm.gltn.net/\"><span style=\" font-size:8pt; text-decoration: underline; color:#0000ff;\">Social Tenure Domain Model (STDM)</span></a><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\"> is a pro poor, gender responsive and participatory land information system developed by the Global Land Tool Network (GLTN). Its one of eighteen land tools being developed, tested and applied by GLTN partners for the promotion of secure land and property rights for all.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"Core_Values\"></a><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">C</span><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">ore Values</span></p>\n"
"<p style=\" margin-top:6px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000; background-color:#ffffff;\">STDM\'s core values and principles are pro-poor, good governance, equity, subsidiarity, sustainability, affordability, systematic large scale, and gender responsiveness.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"The_STDM_Universe\"></a><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">T</span><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">he STDM Universe</span></p>\n"
"<p style=\" margin-top:6px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000; background-color:#ffffff;\">STDM is a pro-poor, participatory and affordable</span><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\"> </span><a href=\"http://gltn.net/index.php/land-tools/introduction-to-land-tools\"><span style=\" font-size:8pt; text-decoration: underline; color:#0000ff;\">land tool</span></a><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\"> that broadens the scope of land administration by incorporating all person/s to land relationships beyond formal/legal land rights, cognisant of the continuum of land rights. STDM has four inter-related components:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\" style=\" margin-top:5px; margin-bottom:1px; margin-left:26px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:13px;\">A new way of thinking about land records</span></li>\n"
"<li style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\" style=\" margin-top:0px; margin-bottom:1px; margin-left:26px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:13px;\">A free and open-source software package to record information about land</span></li>\n"
"<li style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\" style=\" margin-top:0px; margin-bottom:1px; margin-left:26px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:13px;\">An approach of collecting data about land</span></li>\n"
"<li style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\" style=\" margin-top:0px; margin-bottom:1px; margin-left:26px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:13px;\">A way of using and disseminating information about land</span></li></ul>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:1px; margin-left:26px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'sans-serif\'; font-size:8pt; color:#000000;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:1px; margin-left:26px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000; background-color:#ffffff;\">The STDM Universe consists of an extensible data model, conceptual and operational model, database implementation, software modules and an extensible architecture. In detail:</span></p>\n"
"<p style=\" margin-top:3px; margin-bottom:1px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">The data model</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:8px; margin-left:21px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\">The data model has been developed by the members of GLTN. It was tested, extended and maintained to meet real world scenarios. It can be extended to a certain degree to meet the needs of most land administration and natural resource management applications.</span></p>\n"
"<p style=\" margin-top:3px; margin-bottom:1px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">The Enumeration Template</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:8px; margin-left:21px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\">STDM has derived common aspects from existing enumeration questionnaires and aggregated them into a generic model which supports location-based information and settlements profiling.</span></p>\n"
"<p style=\" margin-top:3px; margin-bottom:1px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">The data store</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:8px; margin-left:21px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\">The data store is implemented in an object-relational database with spatial capabilities. It can be extended to a certain degree through the user front end.</span></p>\n"
"<p style=\" margin-top:3px; margin-bottom:1px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">The QGIS Plugin</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:8px; margin-left:21px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000;\">The STDM software is implemented as an extension (plugin) to the Open Source Geographic Information System (GIS) software package, QGIS. This GIS package can be used to analyze, present and combine the collected STDM data on a mapping background and with other geospatial data and maps.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"Future_Plans\"></a><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">F</span><span style=\" font-family:\'sans-serif\'; font-size:8pt; font-weight:600; color:#000000;\">uture Plans</span></p>\n"
"<p style=\" margin-top:6px; margin-bottom:8px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><span style=\" font-family:\'sans-serif\'; font-size:8pt; color:#000000; background-color:#ffffff;\">The STDM software stack and architecture can be adapted to Online versions which could be an alternative as mobile communications connectivity grows.</span></p></body></html>", None))

import resources_rc
