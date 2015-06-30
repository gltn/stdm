# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_property_preview.ui'
#
# Created: Thu Oct 17 13:11:55 2013
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

class Ui_frmPropertyPreview(object):
    def setupUi(self, frmPropertyPreview):
        frmPropertyPreview.setObjectName(_fromUtf8("frmPropertyPreview"))
        frmPropertyPreview.resize(627, 480)
        frmPropertyPreview.setTabPosition(QtGui.QTabWidget.South)
        self.local = QtGui.QWidget()
        self.local.setObjectName(_fromUtf8("local"))
        self.gridLayout = QtGui.QGridLayout(self.local)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.localMap = QgsMapCanvas(self.local)
        self.localMap.setObjectName(_fromUtf8("localMap"))
        self.gridLayout.addWidget(self.localMap, 0, 0, 1, 2)
        self.label = QtGui.QLabel(self.local)
        self.label.setMaximumSize(QtCore.QSize(120, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.cboMapReference = QtGui.QComboBox(self.local)
        self.cboMapReference.setMinimumSize(QtCore.QSize(0, 30))
        self.cboMapReference.setObjectName(_fromUtf8("cboMapReference"))
        self.gridLayout.addWidget(self.cboMapReference, 1, 1, 1, 1)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/local.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmPropertyPreview.addTab(self.local, icon, _fromUtf8(""))
        self.web = QtGui.QWidget()
        self.web.setObjectName(_fromUtf8("web"))
        self.webView = QtWebKit.QWebView(self.web)
        self.webView.setGeometry(QtCore.QRect(19, 19, 561, 401))
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/web.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmPropertyPreview.addTab(self.web, icon1, _fromUtf8(""))

        self.retranslateUi(frmPropertyPreview)
        frmPropertyPreview.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmPropertyPreview)

    def retranslateUi(self, frmPropertyPreview):
        frmPropertyPreview.setWindowTitle(_translate("frmPropertyPreview", "Property Preview", None))
        self.label.setText(_translate("frmPropertyPreview", "Map Reference", None))
        frmPropertyPreview.setTabText(frmPropertyPreview.indexOf(self.local), _translate("frmPropertyPreview", "Local", None))
        frmPropertyPreview.setTabText(frmPropertyPreview.indexOf(self.web), _translate("frmPropertyPreview", "Web", None))

from PyQt4 import QtWebKit
from qgis.gui import QgsMapCanvas
